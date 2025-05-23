from jose import jwt
from datetime import datetime, timedelta, timezone
from main_service.config import get_auth_data
from fastapi import Request, HTTPException, status, Depends, Response
from jose import jwt, JWTError
from datetime import datetime, timezone
from main_service.config import get_auth_data
from main_service.services.users_service import UserService
from main_service.cache_redis import redis_client


def refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=3)
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()
    encode_jwt = jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])
    return encode_jwt


def get_token(request: Request):
    token = request.cookies.get('users_access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    return token

async def add_expired_token_to_cache(user_id: int, token: str) -> None:
    try:
        await redis_client.set(f"expired_{user_id}", f"{token}")
        await redis_client.expire(f"expired_{user_id}", 3600)
        
        print(f"Expired token for user {user_id} added to cache")
        
    except Exception as e:
        raise e


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
    
    user = await UserService.get_user_or_none_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

    expire = payload.get('exp')
    if (not expire):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Срока истечения нет')
    
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