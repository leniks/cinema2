from fastapi import APIRouter, HTTPException, status, Response, Depends

from auth_service.services.users_service import UsersService
from auth_service.schemas.User_schema import RegisterUser, AuthUser
from auth_service.services.auth_service import get_password_hash, authenticate_user_by_username, create_access_token, \
    get_current_user
from auth_service.models.User import User

router = APIRouter(prefix='/auth', tags=['Авторизация'])


@router.post("/register", summary="Создать пользователя")
async def add_user(user_add: RegisterUser) -> dict:
    user = await UsersService.get_user_by_username(username=user_add.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь уже существует'
        )

    user_dict = user_add.model_dump()
    user_dict['password'] = get_password_hash(user_add.password)
    await UsersService.add_user(**user_dict)
    return {'message': 'Вы успешно зарегистрированы!'}


@router.post("/login/", summary="Вход в аккаунт")
async def auth_user(response: Response, user_data: AuthUser):
    user = await authenticate_user_by_username(username=user_data.username, password=user_data.password)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверная почта или пароль')

    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=False)

    try:
        await UsersService.add_session_to_cache(user.id)
    except Exception as e:
        print(f"Error adding session to cache: {e}")

    return {'access_token': access_token}

@router.post("/logout", summary="Выход из аккаунта")
async def logout_user(response: Response, user_data = Depends(get_current_user)):
    response.delete_cookie(key="users_access_token")
    
    try:
        await UsersService.delete_session_from_cache(user_data.id)
    except Exception as e:
        print(f"Error deleting session from cache: {e}")
    
    return {'message': 'Пользователь успешно вышел из системы'}

@router.put("/make_me_admin", summary="Сделать меня администратором")
async def make_admin(user_data = Depends(get_current_user)) -> dict:
    id = int(user_data.id)
    result = await UsersService.make_admin(id=id)
    if result:
        return {'message': 'Пользователь успешно назначен администратором'}
    return {'message': 'Пользователь уже является администратором'}

@router.get("/health", summary="Проверка состояния кэша")
async def health_check():
    await UsersService.check_cache_health()

@router.get("/me")
async def get_me(user_data: User = Depends(get_current_user)):
    data = user_data.to_dict()
    print(data)