from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base
class Scan(Base):
    __tablename__='scans'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    repo: Mapped[str]=mapped_column(String(255),default='inline')
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    findings_json: Mapped[str]=mapped_column(Text)
    summary: Mapped[str]=mapped_column(Text,default='')
