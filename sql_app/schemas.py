from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    price: float
    description: str | None = None
    store_id: int


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int

    class Config:
        orm_mode = True


class StoreBase(BaseModel):
    name: str


class StoreCreate(StoreBase):
    pass


class Store(StoreBase):
    id: int
    items: list[Item] = []

    class Config:
        orm_mode = True


class Country(BaseModel):
    countries: list[str]

    class Config:
        schema_extra = {
            'example': {
                'countries': ['turkey', 'india']
            }
        }


class University(BaseModel):
    country: str | None = None
    web_pages: list[str] = []
    name: str | None = None
    alpha_two_code: str | None = None
    domains: list[str] = []
