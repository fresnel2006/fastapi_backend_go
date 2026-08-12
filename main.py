from fastapi import FastAPI

from Services import GestionsDesRequettesServices
from Routers import Routers
app = FastAPI()

app.include_router(Routers.router)

