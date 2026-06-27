from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn
import os

from routers.query_router import router as query_router

# =========================
# App Init
# =========================

app = FastAPI()

# =========================
# CORS CONFIG (PRODUCTION FIX)
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Routers
# =========================

app.include_router(query_router)

# =========================
# Debug Route
# =========================

@app.get("/debug/ping")
async def debug_ping():
    return {
        "status": "success",
        "message": "UniGuru backend is working"
    }

# =========================
# Swagger Security (JWT)
# =========================

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="UniGuru Intelligence Engine",
        version="2.0.0",
        description="AI backend system",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method].setdefault(
                "security", []
            ).append({"BearerAuth": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# =========================
# Run (Local only)
# =========================

if __name__ == "__main__":
    host = os.getenv("UNIGURU_HOST", "0.0.0.0")
    port = int(os.getenv("UNIGURU_PORT", "8000"))

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )