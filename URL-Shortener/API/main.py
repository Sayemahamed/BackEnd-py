from contextlib import asynccontextmanager

from fastapi.responses import JSONResponse

from API.db import init_db
from API.routes import user_router, auth_router
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="URL Shortener API",
    description="API for shortening URLs",
    version="0.1.0",
    lifespan=lifespan,
)



prefix = "/v1"
app.include_router(user_router, prefix=f"{prefix}/user", tags=["User"])
app.include_router(auth_router, prefix=f"{prefix}/auth", tags=["Auth"])


@app.get("/")
async def root():
    return {"message": "Hello Worlds"}
