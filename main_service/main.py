from fastapi import FastAPI, Request
from main_service.routers.movies_router import router as movies_router
from fastapi.responses import JSONResponse

app = FastAPI()


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": str(exc)},
    )



@app.get("/")
def home_page():
    return {"message": "Cinema main"}


app.include_router(movies_router)