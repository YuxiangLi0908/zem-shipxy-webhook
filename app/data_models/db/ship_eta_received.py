from sqlalchemy import JSON, TIMESTAMP, Column, Integer

from app.data_models.db.base import Base


class ShipEtaReceived(Base):
    __tablename__ = "ship_eta_received"
    __table_args__ = {"schema": "shipxy"}

    id = Column(Integer, primary_key=True, index=True)
    received_at = Column(TIMESTAMP)
    header = Column(JSON)
    body = Column(JSON)
