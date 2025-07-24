from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from urllib.parse import unquote 


router = APIRouter()

@router.get("/api/{path:path}", tags=["Mock API"])
@router.post("/api/{path:path}", tags=["Mock API"])
@router.put("/api/{path:path}", tags=["Mock API"])
@router.delete("/api/{path:path}", tags=["Mock API"])
@router.patch("/api/{path:path}", tags=["Mock API"])
async def dynamic_endpoint(request: Request, path: str):
    decoded_path = unquote(path)
    incoming_path = "/" + decoded_path.strip().lstrip('/')
    method = request.method.upper()

    print(f"Поиск в БД по нормализованному пути: '{incoming_path}' (Метод: {method})")
    
    db_manager = request.app.state.db_manager
    response_data = db_manager.find_response(endpoint=incoming_path, method=method)

    if response_data is not None:
        if isinstance(response_data, int):
            return JSONResponse(status_code=response_data, content=None)
        return JSONResponse(status_code=200, content=response_data)

    raise HTTPException(status_code=404, detail=f"Правило для {method} {incoming_path} не найдено в базе данных")