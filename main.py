from dotenv import load_dotenv
load_dotenv()

from src.conf.database import DATABASE_INIT
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.routes.mods import router as router_mods
from src.routes.users import router as router_users
from src.routes.generos import router as router_generos
from src.routes.imagenes import router as router_imagenes
from src.routes.creditos import router as router_creditos
from src.routes.notifications import router as router_notifications
from src.routes.banners import router as router_banners
from src.routes.mod_statistics import router as router_mod_statistics
from src.routes.collections import router as router_collections
from src.routes.mods_collections import router as router_mods_collections
from src.routes.mod_genres import router as router_mod_genres
from src.middleware.context import user_context_middleware
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from collections import defaultdict
import time

db = DATABASE_INIT()

# Configurar rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="DDLC Mods API",
    version="1.0.0"
)

# Agregar el rate limiter al estado de la app
app.state.limiter = limiter

# Agregar middleware de slowapi
app.add_middleware(SlowAPIMiddleware)

# Handler personalizado para errores de rate limit
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={
            "response": "error",
            "message": "Demasiadas peticiones. Límite: 100 peticiones por minuto por IP",
            "detail": str(exc.detail)
        },
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agregar middleware para contexto de usuario
app.middleware("http")(user_context_middleware)

app.include_router(router_mods, prefix="/mod", tags=["mods"])
app.include_router(router_users, prefix="/users", tags=["users"])
app.include_router(router_generos, prefix="/genres", tags=["genres"])
app.include_router(router_imagenes, prefix="/images", tags=["images"])
app.include_router(router_creditos, prefix="/credits", tags=["credits"])
app.include_router(router_notifications, prefix="/notifications", tags=["notifications"])
app.include_router(router_banners, prefix="/banners", tags=["banners"])
app.include_router(router_mod_statistics, prefix="/statistics", tags=["statistics"])
app.include_router(router_collections, prefix="/collections", tags=["collections"])
app.include_router(router_mods_collections, prefix="/mods-collections", tags=["mods-collections"])
app.include_router(router_mod_genres, prefix="/mods-genres", tags=["mods-genres"])

# Ensure all models are imported before creating tables
import src.models.generos
import src.models.imagen
import src.models.users
import src.models.mods
import src.models.credits
import src.models.notifications
import src.models.banners
import src.models.mod_statistic
import src.models.collection
import src.models.mods_collection
import src.models.mod_genre

db.BASE_TYPE.metadata.create_all(bind=db.create_engine())

@app.get("/")
def root():
    return {"message": "API funcionando"}