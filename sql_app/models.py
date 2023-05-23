from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship

from config.db import Base


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), nullable=False, unique=True, index=True)
    price = Column(Float(precision=2), nullable=False)
    description = Column(String(200))
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=False)

    def __repr__(self) -> str:
        return f"ItemModel(name={self.name}, price={self.price}, store_id={self.store_id}"

    def __str__(self) -> str:
        return self.name


class Store(Base):
    __tablename__ = 'stores'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), nullable=False, unique=True)

    items = relationship('Item', primaryjoin='Store.id == Item.store_id', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f"Store(name={self.name})"

    def __str__(self) -> str:
        return self.name
