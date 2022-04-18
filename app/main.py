import time
from pathlib import Path

from fastapi import FastAPI, APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from app import crud
from app.api import deps
from app.api.api_v1.api import api_router
from app.core.config import settings


from starlette.templating import _TemplateResponse


BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

root_router = APIRouter()
app = FastAPI(title="Recipe API", openapi_url="/openapi.json")


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_origin_regex=settings.BACKEND_CORS_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Updated to serve a Jinja2 template
# https://www.starlette.io/templates/
# https://jinja.palletsprojects.com/en/3.0.x/templates/#synopsis
@root_router.get("/", status_code=200)
def root(
    request: Request,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Root GET
    """
    recipes = crud.recipe.get_multi(db=db, limit=10)
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request, "recipes": recipes},
    )


# What does this do?
# Very cool - tacks on an http header to the response to my API call.
# Like pre- and post-script. https://fastapi.tiangolo.com/tutorial/middleware/
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# This gives the "/api/v1" prefix
# e.g /api/v1/recipes
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(root_router)



if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    # Error thrown on app due to how Starlette does typing vs uvicorn.
    # https://github.com/tiangolo/fastapi/issues/3927
    # Uvicorn has recently added typing for it's configuration and it wants an: ASGIApplication, Callable, or str.
    # FastAPI extends from Starlette: https://github.com/tiangolo/fastapi/blob/master/fastapi/applications.py#L31 and the issue here is that Starlette is not typed to an ASGIApplication
    # https://github.com/encode/starlette/issues/1217
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug") # pyright: reportGeneralTypeIssues=false