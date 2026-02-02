from sqlalchemy import Column, String, Text

from core.schemas.base import AppDBModel


class Item(AppDBModel):
    __tablename__ = "item"

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
