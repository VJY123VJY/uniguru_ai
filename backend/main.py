from service.api import app
from routers.query_router import router as query_router
import uvicorn
import os

from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# =========================
# CORS Configuration
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",

        # Add your Render frontend URL here
        # "https://your-frontend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Register Routers
# =========================

app.include_router(query_router)

# =========================
# Debug Endpoint
# =========================

@app.get("/debug/ping")
async def debug_ping():
    return {
        "status": "success",
        "message": "UniGuru Modular Router is reachable"
    }

# =========================
# Swagger Auth Configuration
# =========================

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="UniGuru Intelligence Engine",
        version="2.0.0",
        description="Sovereign AI reasoning engine with deterministic priority.",
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
# Run App
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