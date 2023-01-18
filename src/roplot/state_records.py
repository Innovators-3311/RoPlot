from roplot import FieldPowerPlay, Robot
from .database import Base

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, desc
from sqlalchemy.orm import Session

from datetime import datetime

RUNTIME_FIELD="runTime"


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

    @classmethod
    def get_latest(cls, session: Session, **kwargs) -> Base:
        """Get the latest instance of state from the database.

        Args:
            session (sqlalchemy.session): A database session from which to query
            **kwargs: parameters sent to filter_by (e.g. type="CombinedLocalizer")

        Returns:
            StateRecord: the latest StateRecord object in that database. 
        """
        return session.query(StateRecord).filter_by(**kwargs).order_by(desc( StateRecord.id )).limit(1).first()


