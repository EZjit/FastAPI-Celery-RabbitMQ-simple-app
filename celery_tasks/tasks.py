from celery import shared_task

from api import universities


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True,
             retry_kwargs={'max_retries': 5}, name='universities:get_all_universities_task')
def get_all_universities_task(self, countries: list[str]):
    data: dict = {}
    for country in countries:
        data.update(universities.get_all_universities_for_country(country))
    return data


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True,
             retry_kwargs={'max_retries': 5}, name='universities:get_university_task')
def get_university_task(self, country: str):
    return universities.get_all_universities_for_country(country)
