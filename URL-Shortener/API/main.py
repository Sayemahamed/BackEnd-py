from fastapi import FastAPI
from contextlib import asynccontextmanager
from API.db import init_db
from API.celery import test



@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="URL Shortener API",
    description="API for shortening URLs",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    test.delay()
    return {"message": "Hello Worlds"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}