from logging.config import fileConfig
from alembic import context
import os
import pkgutil
import sys

# Add the project's src directory to the sys.path to allow for package imports
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '../')))

# Import the engine configuration utility from the project's source
from database import get_engine, get_database_url

# Assuming all your models inherit from 'Base' which is imported from the project's source
from entities.base_entity import BaseEntity

# Set the target metadata to the Base's metadata for Alembic migrations
target_metadata = BaseEntity.metadata

# Define the path to the entities directory where the model files are located
entities_directory = os.path.join(os.path.dirname(__file__), '../entities')

# Dynamically import all modules in the entities directory to register the Base classes
# This is needed for Alembic to detect all the model classes for migration generation
for (_, name, _) in pkgutil.iter_modules([entities_directory]):
    __import__('entities.' + name)

# Alembic configuration object is obtained from the Alembic context
config = context.config

# Optionally set up logging using the configuration file if it's specified
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the SQLAlchemy database URL in the Alembic configuration
config.set_main_option('sqlalchemy.url', get_database_url())

# Define a function to run migrations in an offline mode
# This is typically used for generating SQL scripts for database changes
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()

# Define a function to run migrations in an online mode
# This directly connects to the database and applies the migrations
def run_migrations_online():
    # Get the SQLAlchemy engine from the project's configuration
    connectable = get_engine()

    # Establish a connection and configure the context for Alembic
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        # Run migrations within a transaction
        with context.begin_transaction():
            context.run_migrations()

# Check if the context is configured for offline mode and run the appropriate function
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()