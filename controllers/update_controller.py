from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Any
from urllib.parse import unquote 

class UpdateRequest(BaseModel):
    method: str
    response: Any

router = APIRouter()

@router.put("/set/{endpoint:path}", tags=["Update Responses"])
async def update_mock_response(request: Request, endpoint: str, update_data: UpdateRequest):
    decoded_path = unquote(endpoint)
    full_endpoint = "/" + decoded_path.strip().lstrip('/')
    
    db_manager = request.app.state.db_manager
    
    success = db_manager.update_response(
        endpoint=full_endpoint,
        method=update_data.method,
        new_response=update_data.response
    )
    
    if success:
        return {"message": f"Ответ для {update_data.method.upper()} {full_endpoint} успешно обновлен."}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Запись для {update_data.method.upper()} {full_endpoint} не найдена и не была обновлена."
        )
