# 1. Import Libraries
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base

# 2. Load Environment Variables
load_dotenv()

# 3. Configure PostgreSQL Connection
SQLALCHEMY_DATABASE_URL=URL.create(
    drivername="postgresql+psycopg2",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.getenv("DB_HOST","localhost"),
    port=int(os.getenv("DB_PORT","5432")),
    database=os.environ["DB_NAME"]
)

# 4. Create Database Engine
engine=create_engine(SQLALCHEMY_DATABASE_URL,pool_pre_ping=True)

# 5. Create Database Session
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

# 6. Create Base Class for ORM Models
Base=declarative_base()
