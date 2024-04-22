from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from middlewares import CustomHeaderMiddleware
from fastapi_limiter import FastAPILimiter
from src.conf.config import settings
from src.routes import contacts, auth, users
from middlewares import (BlackListMiddleware, CustomCORSMiddleware,
                         CustomHeaderMiddleware, UserAgentBanMiddleware,
                         WhiteListMiddleware)

import redis.asyncio as redis
import uvicorn

app = FastAPI()

app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.add_middleware(CustomHeaderMiddleware)
# app.add_middleware(BlackListMiddleware)
# app.add_middleware(CustomCORSMiddleware)
# app.add_middleware(UserAgentBanMiddleware)
# app.add_middleware(WhiteListMiddleware)



# app.mount("/static", StaticFiles(directory='src/static'), name="static")

@app.on_event("startup")
async def startup():

    """
    The read_root function is a function that returns the root page of the website.
        It takes in a request object and returns an HTML response with the index.html template.
    
    :param request: Request: Pass the request object to the template
    :return: A templateresponse object, which is a special type of response object
    :doc-author: Trelent
    """
    r = await redis.Redis(host=settings.REDIS_DOMAIN, port=settings.REDIS_PORT, db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)

@app.get("/")
def read_root():
    """
    Root endpoint returning a greeting message.

    :return: dict: A dictionary containing a greeting message.
    """
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)