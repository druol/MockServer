from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Any


class UpdateRequest(BaseModel):
    method: str
    response: Any

router = APIRouter()

@router.put("/set/{endpoint:path}", tags=["Update Responses"])
async def update_mock_response(request: Request, endpoint: str, update_data: UpdateRequest):

    full_endpoint = "/" + endpoint
    
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
