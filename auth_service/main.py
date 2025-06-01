from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from auth_service.routers.users_router import router as users_router

app = FastAPI()

# Настройка CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все origins для отладки
    allow_credentials=False,  # Отключаем credentials для отладки
    allow_methods=["*"],
    allow_headers=["*"],
)

# Дополнительный middleware для CORS (на случай если стандартный не работает)
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

app.include_router(users_router)

@app.get("/")
def home_page():
    return {"message": "auth service"}