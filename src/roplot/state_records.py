from roplot import FieldPowerPlay, Robot, StateRecord

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, desc

from datetime import datetime

RUNTIME_FIELD="runTime"

Base = declarative_base()

class StateRecord(Base):
    __tablename__ = "StateRecords"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    runtime = Column(Float)
    record = Column(JSON)

    def __init__(self, record):
        self.record = record
        self.timestamp = datetime.now()
        self.runtime = float(record.get(RUNTIME_FIELD))

    def __repr__(self):
        return f"<StateRecord at {self.timestamp.isoformat()}>"

    @classmethod
    def get_latest(cls, session, **kwargs) -> Base:
        """Get the latest instance of state from the database.

        Args:
            session (sqlalchemy.session): A database session from which to query
            **kwargs: parameters sent to filter_by (e.g. type="CombinedLocalizer")

        Returns:
            StateRecord: the latest StateRecord object in that database. 
        """
        return session.query(StateRecord).filter_by(**kwargs).order_by(desc( StateRecord.id )).limit(1).first()


