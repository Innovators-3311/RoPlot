from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATA_PATH='data'
TODAY = datetime.now().strftime("%Y-%m-%d")
ENGINE = create_engine(f"sqlite:///{DATA_PATH}/{TODAY}.sqlite")
SessionLocal = sessionmaker(bind=ENGINE)

Base = declarative_base()