from fastapi import FastAPI
from order_routes import order_router
from auth_routes import auth_router
from fastapi_jwt_auth import AuthJWT
from schemas import Settings
from core.database import SessionLocal


app = FastAPI()


@AuthJWT.load_config
def set_config():
    return Settings()


app.include_router(order_router)
app.include_router(auth_router)
