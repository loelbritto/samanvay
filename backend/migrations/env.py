from alembic import context
from app.config import Settings
from app.database import make_database
from app.models import Base

target_metadata = Base.metadata

if context.is_offline_mode():
    context.configure(url=Settings.from_env().database_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    supplied_connection=context.config.attributes.get('connection')
    if supplied_connection is not None:
        context.configure(connection=supplied_connection,target_metadata=target_metadata,render_as_batch=True)
        with context.begin_transaction():context.run_migrations()
    else:
        engine, _ = make_database(Settings.from_env())
        with engine.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
            with context.begin_transaction():
                context.run_migrations()
