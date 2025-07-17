import json
from fastapi import Request, Response


request_counter = 0
async def history_middleware(request: Request, call_next):
    global request_counter
    
    if request.url.path.startswith("/api/_request-history"):
        return await call_next(request)

    request_counter += 1
    request_id = request_counter
    
    response = await call_next(request)

    body_bytes = b""
    async for chunk in response.body_iterator:
        body_bytes += chunk
    
    try:
        body_json = json.loads(body_bytes) if body_bytes else None
    except json.JSONDecodeError:
        body_json = None

    record = {
        "id": request_id,
        "method": request.method,
        "path": request.url.path,
        "query": dict(request.query_params),
        "status_code": response.status_code,
        "response_body": json.dumps(body_json, ensure_ascii=False) if body_json is not None else None,
        "client": request.client.host,
    }
    
    db_manager = request.app.state.db_manager
    db_manager.add_history_record(record)

    return Response(
        content=body_bytes,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )
