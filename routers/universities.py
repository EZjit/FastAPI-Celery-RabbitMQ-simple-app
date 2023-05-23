from celery import group
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from api import universities
from celery_tasks.tasks import get_university_task, get_all_universities_task
from config.celery_utils import get_task_info
from sql_app.schemas import Country

router = APIRouter(prefix='/universities_background', tags=['University-background'])


@router.post('/')
def get_universities(country: Country):
    data: dict = {}
    for cntr in country.countries:
        data.update(universities.get_all_universities_for_country(cntr))
    return data


@router.post('/async')
async def get_universities_async(country: Country):
    task = get_all_universities_task.apply_async(args=[country.countries])
    return JSONResponse({'task_id': task.id})


@router.get('/task/{task_id}')
async def get_task_status(task_id: str):
    return get_task_info(task_id)


@router.post('/parallel')
async def get_universities_parallel(country: Country):
    data: dict = {}
    tasks = []
    for cntr in country.countries:
        tasks.append(get_university_task.s(cntr))
    job = group(tasks)
    result = job.apply_async()
    returned_values = result.get(disable_sync_subtasks=False)
    for result in returned_values:
        data.update(result)
    return data
