from uuid import uuid4
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Item(Base):
    __tablename__ = "items"

    id: Mapped[str]   = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
