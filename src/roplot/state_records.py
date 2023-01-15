from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON

from datetime import datetime

RUNTIME_FIELD="runTime"

Base = declarative_base()

class StateRecord(Base):
    __tablename__ = "StateRecords"

    id = Column(Integer, primary_key=True)
    type = Column(String)
    timestamp = Column(DateTime)
    runtime = Column(Float)
    record = Column(JSON)

    def __init__(self, record):
        self.record = record
        self.type = record.get("type", "none")
        self.timestamp = datetime.now()
        self.runtime = float(record.get(RUNTIME_FIELD))

    def __repr__(self):
        return f"<StateRecord at {self.timestamp.isoformat()}>"


