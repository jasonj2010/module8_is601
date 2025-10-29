# main.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
from fastapi.exceptions import RequestValidationError
from app.operations import add, subtract, multiply, divide
import uvicorn
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ============================================================
# Logging setup
# ============================================================

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

logger = logging.getLogger("fastapi-calculator")
logger.setLevel(logging.INFO)

# avoid duplicate handlers on reload
if not logger.handlers:
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=512_000, backupCount=2, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# ============================================================
# FastAPI app setup
# ============================================================

app = FastAPI(title="FastAPI Calculator with Logging")
templates = Jinja2Templates(directory="templates")

# ============================================================
# Models
# ============================================================

class OperationRequest(BaseModel):
    a: float = Field(..., description="The first number")
    b: float = Field(..., description="The second number")

    @field_validator('a', 'b')
    def validate_numbers(cls, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Both a and b must be numbers.")
        return value


class OperationResponse(BaseModel):
    result: float = Field(..., description="The result of the operation")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")

# ============================================================
# Middleware – log every request and response
# ============================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"REQ {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"RESP {request.method} {request.url.path} -> {response.status_code}")
        return response
    except Exception as e:
        logger.exception(f"Unhandled exception for {request.method} {request.url.path}: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})

# ============================================================
# Exception Handlers
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException on {request.url.path}: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = "; ".join([f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()])
    logger.error(f"ValidationError on {request.url.path}: {error_messages}")
    return JSONResponse(status_code=400, content={"error": error_messages})

# ============================================================
# Routes
# ============================================================

@app.get("/")
async def read_root(request: Request):
    """Serve the index.html template."""
    logger.info("GET / (root template served)")
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/add", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def add_route(operation: OperationRequest):
    """Add two numbers."""
    try:
        result = add(operation.a, operation.b)
        logger.info(f"ADD: {operation.a} + {operation.b} = {result}")
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Add Operation Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/subtract", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def subtract_route(operation: OperationRequest):
    """Subtract two numbers."""
    try:
        result = subtract(operation.a, operation.b)
        logger.info(f"SUBTRACT: {operation.a} - {operation.b} = {result}")
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Subtract Operation Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/multiply", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def multiply_route(operation: OperationRequest):
    """Multiply two numbers."""
    try:
        result = multiply(operation.a, operation.b)
        logger.info(f"MULTIPLY: {operation.a} * {operation.b} = {result}")
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Multiply Operation Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/divide", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def divide_route(operation: OperationRequest):
    """Divide two numbers."""
    try:
        result = divide(operation.a, operation.b)
        logger.info(f"DIVIDE: {operation.a} / {operation.b} = {result}")
        return OperationResponse(result=result)
    except ValueError as e:
        logger.warning(f"Divide Operation Warning: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Divide Operation Internal Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# ============================================================
# Entrypoint
# ============================================================

if __name__ == "__main__":
    logger.info("Starting FastAPI Calculator app on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
