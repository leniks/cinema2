from fastapi import APIRouter, HTTPException, status, Response, Depends

from app.services.users_service import UsersService
from app.schemas.User_schema import RegisterUser, AuthUser
from app.services.auth_service import get_password_hash, authenticate_user_by_username, create_access_token, \
    get_current_user

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

    return {'access_token': access_token}

@router.post("/logout", summary="Выход из аккаунта")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}

@router.put("/make_me_admin", summary="Сделать меня администратором")
async def make_admin(user_data = Depends(get_current_user)) -> dict:
    id = int(user_data.id)
    result = await UsersService.make_admin(id=id)
    if result:
        return {'message': 'Пользователь успешно назначен администратором'}
    return {'message': 'Пользователь уже является администратором'}