from fastapi import APIRouter, HTTPException, Request


router = APIRouter()

@router.get("/api/_request-history/{req_id}")
async def get_request_record(req_id: int, request: Request):
    db_manager = request.app.state.db_manager
    record = db_manager.get_history_record_by_id(req_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Запись не найдена в базе данных")
    return record

@router.get("/api/_request-history")
async def list_request_history(request: Request):
    db_manager = request.app.state.db_manager
    return db_manager.get_history()