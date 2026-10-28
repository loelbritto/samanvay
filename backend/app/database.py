from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from .config import Settings


def make_database(settings: Settings):
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False, "timeout": 15}, echo=False)

    @event.listens_for(engine, "connect")
    def configure_connection(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")

    return engine, sessionmaker(engine, expire_on_commit=False)
