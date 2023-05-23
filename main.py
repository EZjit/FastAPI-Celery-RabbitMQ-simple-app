import time

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from config.celery_utils import create_celery
from routers import universities

from config.db import get_db, engine
import sql_app.models as models
import sql_app.schemas as schemas
from sql_app.repositories import ItemRepo, StoreRepo


def create_app() -> FastAPI:
    current_app = FastAPI(title='FastAPI+Celery+RabbitMQ project. Task processing w/ Celery and RabbitMQ')
    current_app.celery_app = create_celery()
    current_app.include_router(universities.router)
    return current_app


app = create_app()
celery = app.celery_app

models.Base.metadata.create_all(bind=engine)


@app.exception_handler(Exception)
def validation_exception_handler(request, err):
    base_error_message = f"Failed to execute: {request.method}: {request.url}"
    return JSONResponse(status_code=400, content={"message": f"{base_error_message}. Detail: {err}"})


@app.post('/items/', tags=['Item'], response_model=schemas.Item, status_code=201)
async def create_item(item_request: schemas.ItemCreate, db: Session = Depends(get_db)):
    new_item = ItemRepo.fetch_by_name(db, name=item_request.name)
    if new_item:
        raise HTTPException(status_code=400, detail='Item already exists!')

    return await ItemRepo.create(db=db, item=item_request)


@app.get('/items/', tags=['Item'], response_model=list[schemas.Item])
def get_all_items(name: str | None = None, db: Session = Depends(get_db)):
    if name:
        items = []
        item = ItemRepo.fetch_by_name(db, name)
        items.append(item)
        return items
    else:
        return ItemRepo.fetch_all(db)


@app.get('/items/{item_id}', tags=['Item'], response_model=schemas.Item)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = ItemRepo.fetch_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail='Item with given ID not found')
    return item


@app.delete('/items/{item_id}', tags=['Item'])
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = ItemRepo.fetch_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail='Item with given ID not found')
    await ItemRepo.delete(db, item_id)
    return 'Item deleted successfully!'


@app.put('/items/{item_id}', tags=['Item'], response_model=schemas.Item)
async def update_item(item_id: int, item_request: schemas.Item, db: Session = Depends(get_db)):
    item = ItemRepo.fetch_by_id(db, item_id)
    if item:
        update_item_encoded = jsonable_encoder(item_request)
        item.name = update_item_encoded['name']
        item.price = update_item_encoded['price']
        item.description = update_item_encoded['description']
        item.store_id = update_item_encoded['store_id']
        return await ItemRepo.update(db=db, item_data=item)
    else:
        raise HTTPException(status_code=400, detail='Item with given ID not found!')


@app.post('/stores/', tags=['Store'], response_model=schemas.Store, status_code=201)
async def create_store(store_request: schemas.StoreCreate, db: Session = Depends(get_db)):
    new_store = StoreRepo.fetch_by_name(db, name=store_request.name)
    if new_store:
        raise HTTPException(status_code=400, detail='Store already exists!')

    return await StoreRepo.create(db=db, store=store_request)


@app.get('/stores/', tags=['Store'], response_model=list[schemas.Store])
def get_all_stores(name: str | None = None, db: Session = Depends(get_db)):
    if name:
        stores = []
        store = StoreRepo.fetch_by_name(db, name)
        stores.append(store)
        return stores
    else:
        return StoreRepo.fetch_all(db)


@app.get('/stores/{store_id}', tags=['Store'], response_model=schemas.Store)
def get_store(store_id: int, db: Session = Depends(get_db)):
    store = StoreRepo.fetch_by_id(db, store_id)
    if store is None:
        raise HTTPException(status_code=404, detail='Store with given ID not found')
    return store


@app.delete('/stores/{store_id}', tags=['Store'])
async def delete_store(store_id: int, db: Session = Depends(get_db)):
    store = StoreRepo.fetch_by_id(db, store_id)
    if store is None:
        raise HTTPException(status_code=404, detail='Store with given ID not found')
    await StoreRepo.delete(db, store_id)
    return 'Store deleted successfully!'


@app.patch('/stores/{store_id}', tags=['Store'], response_model=schemas.Store)
async def update_store(store_id: int, store_request: schemas.StoreBase, db: Session = Depends(get_db)):
    store = StoreRepo.fetch_by_id(db, store_id)
    if store:
        update_store_encoded = jsonable_encoder(store_request)
        store.name = update_store_encoded['name']
        return await StoreRepo.update(db=db, store_data=store)
    else:
        raise HTTPException(status_code=400, detail='Store with given ID not found!')


from api import universities
import asyncio

@app.get('/universities/', tags=['University'])
def get_universities() -> dict:
    data: dict = {}
    data.update(universities.get_all_universities_for_country('turkey'))
    data.update(universities.get_all_universities_for_country('india'))
    data.update(universities.get_all_universities_for_country('australia'))
    return data

@app.get('/universities/async', tags=['University'])
async def get_universities_async() -> dict:
    data: dict = {}
    await asyncio.gather(universities.get_all_universities_for_country_async('turkey', data),
                         universities.get_all_universities_for_country_async('india', data),
                         universities.get_all_universities_for_country_async('australia', data))
    return data

@app.middleware('http')
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers['X-Process-Time'] = f'{process_time:0.4f} sec'
    return response
