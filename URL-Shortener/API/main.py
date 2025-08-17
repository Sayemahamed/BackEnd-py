from contextlib import asynccontextmanager

from API.db import init_db
from API.routes import user_router
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

app.include_router(user_router, prefix="/user", tags=["User"])


@app.get("/")
async def root():
    return {"message": "Hello Worlds"}
