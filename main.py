from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers.products import router as products_router
from app.routers.users import router as users_router

app = FastAPI()

# Mount routers — equivalent of Django's include() in urls.py.
app.include_router(users_router)
app.include_router(products_router)

app.mount("/static", StaticFiles(directory="public"), name="public")

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def root():
    return {"Hello": "World"}
