from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Services import GestionsDesRequettesServices
from Routers import Routers

app = FastAPI()

# CORS : autorise ton frontend (et pour l'instant tout le monde, le temps de
# stabiliser) à appeler cette API depuis un domaine différent du backend.
# Sans ça, le navigateur bloque silencieusement tous les fetch() du frontend
# même si l'API répond parfaitement bien (le "Impossible de joindre le
# référentiel" que tu viens de voir en est un exemple typique).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # ⚠️ à restreindre plus tard, voir note en bas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(Routers.router)