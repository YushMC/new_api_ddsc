from dotenv import load_dotenv
load_dotenv()

from src.conf.database import DATABASE_INIT
from fastapi import FastAPI
from src.routes.mods import router as router_mods
from src.routes.users import router as router_users
from src.routes.generos import router as router_generos
from src.routes.imagenes import router as router_imagenes
from src.routes.creditos import router as router_creditos
from src.middleware.context import user_context_middleware

db = DATABASE_INIT()

app = FastAPI(
    title="DDLC Mods API",
    version="1.0.0"
)

# Agregar middleware para contexto de usuario
app.middleware("http")(user_context_middleware)

app.include_router(router_mods, prefix="/mod", tags=["mods"])
app.include_router(router_users, prefix="/users", tags=["users"])
app.include_router(router_generos, prefix="/genres", tags=["genres"])
app.include_router(router_imagenes, prefix="/images", tags=["images"])
app.include_router(router_creditos, prefix="/credits", tags=["credits"])

# Ensure all models are imported before creating tables
import src.models.generos
import src.models.imagen
import src.models.users
import src.models.mods
import src.models.credits

db.BASE_TYPE.metadata.create_all(bind=db.create_engine())

@app.get("/")
def root():
    return {"message": "API funcionando"}