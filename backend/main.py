import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_swagger import patch_fastapi
from database import create_db
from routes import router as contact_router
from auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database...")
    create_db()
    print("Database initialized successfully.")
    yield
    print("Shutting down application...")

app = FastAPI(
    title="Contact Management API with Auth",
    description="Protected contact API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url=None,
    swagger_ui_oauth2_redirect_url=None
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round(time.time() - start, 3)
    print(
        f"[{request.method}] {request.url.path}"
        f" -> {response.status_code} ({duration}s)"
    )
    return response


patch_fastapi(app, docs_url="/swagger")


app.include_router(auth_router)
app.include_router(contact_router, prefix="/api/v1")
