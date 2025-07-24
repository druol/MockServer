import sqlite3
import DatabaseManager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, HTTPException, Request, Response
from urllib.parse import unquote 
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
import json
from pathlib import Path
import os
from fastapi.responses import JSONResponse
import uvicorn
from controllers import history_controller, mock_controller, update_controller
from middleware.cookies_middleware import cookies_middleware
from middleware.history_middleware import history_middleware


def get_endpoints_file():
    # Check environment variable first
    if file_path := os.getenv("ENDPOINTS_FILE"):
        return Path(file_path)
    
    # Check command-line argument
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "--file":
        try:
            return Path(os.sys.argv[2])
        except IndexError:
            raise ValueError("Missing filename after --file")
    
    # Default path
    default_path = Path("endpoints.json")
    if default_path.exists():
        return default_path
    
    raise RuntimeError("No endpoints file specified. Use ENDPOINTS_FILE environment variable or --file argument")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- Старт жизненного цикла приложения ---")
    endpoints_file_path = get_endpoints_file()

    db_manager = DatabaseManager.DatabaseManager(
        db_name="database.db", 
        json_path=str(endpoints_file_path)
    )
    db_manager.run_full_setup_cycle()
    app.state.db_manager = db_manager
    print("--- Менеджер БД успешно инициализирован и сохранен в app.state ---")
    yield

app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html>
        <head>
            <link type="text/css" rel="stylesheet" href="/static/swagger-ui.css">
            <title>Swagger UI</title>
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="/static/swagger-ui-bundle.js"></script>
            <script>
                const ui = SwaggerUIBundle({
                    url: '/openapi.json',
                    dom_id: '#swagger-ui',
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ],
                    layout: "BaseLayout"
                })
            </script>
        </body>
        </html>
        """,
        status_code=200,
    )


app.add_middleware(BaseHTTPMiddleware, dispatch = history_middleware)
app.add_middleware(BaseHTTPMiddleware, dispatch = cookies_middleware)

app.include_router(history_controller.router)
app.include_router(mock_controller.router)
app.include_router(update_controller.router) 


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

