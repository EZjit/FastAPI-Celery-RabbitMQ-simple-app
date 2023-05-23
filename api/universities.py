import json
from sql_app.schemas import University

import httpx


def get_all_universities_for_country(country: str) -> dict:
    url = 'http://universities.hipolabs.com/search'
    params = {'country': country}
    client = httpx.Client()
    response = client.get(url, params=params)
    response_json = json.loads(response.text)
    universities = []
    for university in response_json:
        university_obj = University.parse_obj(university)
        universities.append(university_obj)
    return {country: universities}


async def get_all_universities_for_country_async(country: str, data: dict) -> None:
    url = 'http://universities.hipolabs.com/search'
    params = {'country': country}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response_json = json.loads(response.text)
        universities = []
        for university in response_json:
            university_obj = University.parse_obj(university)
            universities.append(university_obj)
    data[country] = universities
