import json
from fastapi import Request, Response, Cookie
import random



async def cookies_middleware(request: Request, call_next):
    question_session = "QESSIONID" in request.cookies

    response = await call_next(request)

    #if (not question_session):
    session_id = random.randrange(0, 255)

    response.set_cookie(
        key = "QESSIONID",
        value = session_id,
        httponly = True,
        secure = True,
        samesite = "Lax",
        max_age = 1800
    )
        
    return response
