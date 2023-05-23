from sqlalchemy.orm import Session

from . import models, schemas


class ItemRepo:
    @staticmethod
    async def create(db: Session, item: schemas.ItemCreate):
        new_item = models.Item(name=item.name, price=item.price, description=item.description, store_id=item.store_id)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

    @staticmethod
    def fetch_by_id(db: Session, item_id: int):
        return db.query(models.Item).filter(models.Item.id == item_id).first()

    @staticmethod
    def fetch_by_name(db: Session, name: str):
        return db.query(models.Item).filter(models.Item.name == name).first()

    @staticmethod
    def fetch_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.Item).offset(skip).limit(limit).all()

    @staticmethod
    async def delete(db: Session, item_id: int):
        item = db.query(models.Item).filter_by(id=item_id).first()
        db.delete(item)
        db.commit()

    @staticmethod
    async def update(db: Session, item_data):
        updated_item = db.merge(item_data)
        db.commit()
        return updated_item


class StoreRepo:
    @staticmethod
    async def create(db: Session, store: schemas.StoreCreate):
        new_store = models.Store(name=store.name)
        db.add(new_store)
        db.commit()
        db.refresh(new_store)
        return new_store

    @staticmethod
    def fetch_by_id(db: Session, store_id: int):
        return db.query(models.Store).filter(models.Store.id == store_id).first()

    @staticmethod
    def fetch_by_name(db: Session, name: str):
        return db.query(models.Store).filter(models.Store.name == name).first()

    @staticmethod
    def fetch_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.Store).offset(skip).limit(limit).all()

    @staticmethod
    async def delete(db: Session, store_id: int):
        store = db.query(models.Store).filter_by(id=store_id).first()
        db.delete(store)
        db.commit()

    @staticmethod
    async def update(db: Session, store_data):
        updated_store = db.merge(store_data)
        db.commit()
        return updated_store
