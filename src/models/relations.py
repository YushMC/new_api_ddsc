from sqlalchemy import Table, Column, Integer, ForeignKey, Boolean
from src.conf.database import DATABASE_INIT
from src.conf.all_keys import TABLE_NAMES, QUERY_PARAMS

__Base = DATABASE_INIT().BASE_TYPE

mods_genres = Table(
    TABLE_NAMES.MODS_GENEROS,
    __Base.metadata,
    Column("id",Integer, primary_key=True, index=True, autoincrement="auto"),
    Column("mod_id", Integer, ForeignKey(TABLE_NAMES.MODS + QUERY_PARAMS.JOIN_BY_ID)),
    Column("genre_id", Integer, ForeignKey(TABLE_NAMES.GENEROS + QUERY_PARAMS.JOIN_BY_ID)),
    Column("is_active", Boolean, default=True)
)