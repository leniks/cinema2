from passlib.context import CryptContext

from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from auth_service.config import get_auth_data
from auth_service.services.users_service import UsersService

from fastapi import Request, HTTPException, status, Depends, Response
from auth_service.services.users_service import UsersService
from auth_service.cache_redis import redis_client


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def add_expired_token_to_cache(user_id: int, token: str) -> None:
    try:
        await redis_client.set(f"expired_{user_id}", f"{token}")
        await redis_client.expire(f"expired_{user_id}", 3600)
        
        print(f"Expired token for user {user_id} added to cache")
        
    except Exception as e:
        raise e  

def refresh_token(data: dict) -> str:
    return create_access_token(data)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=3)
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()
    encode_jwt = jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])
    return encode_jwt

async def authenticate_user_by_username(username: str, password: str):
    user = await UsersService.get_user_by_username(username=username)
    if not user or verify_password(plain_password=password, hashed_password=user.password) is False:
        return None
    return user


def get_token(request: Request):
    token = request.cookies.get('users_access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    return token


async def get_current_user(token: str = Depends(get_token), response: Response = Response):
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']], options={"verify_exp": False})
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')
    
    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не найден ID пользователя')
    
    if await redis_client.get(f"expired_{user_id}") == token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Вы не авторизованы или сессия истекла')
    
    user = await UsersService.get_user_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

    expire = payload.get('exp')
    if (not expire):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Срока истечения токена нет')
    
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (expire_time < datetime.now(timezone.utc)):
        print("Token expired")
        
        if await redis_client.exists(f"user_{user_id}"):
            await add_expired_token_to_cache(user_id, token)

            access_token = refresh_token({"sub": str(user.id)})
            response.set_cookie(key="users_access_token", value=access_token, httponly=False)
            print(f"Token for user {user_id} refreshed")
        
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Вы не авторизованы или сессия истекла')

    return user