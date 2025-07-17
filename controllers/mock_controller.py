from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def dynamic_endpoint(request: Request, path: str):
    incoming_path = "/" + path
    method = request.method.upper()
    
    db_manager = request.app.state.db_manager
    response_data = db_manager.find_response(endpoint=incoming_path, method=method)

    if response_data is not None:
        if isinstance(response_data, int):
            return JSONResponse(status_code=response_data, content=None)
        return JSONResponse(status_code=200, content=response_data)

    raise HTTPException(status_code=404, detail=f"Правило для {method} {incoming_path} не найдено в базе данных")