import asyncio
import csv
import os
from datetime import datetime

import asyncpg

from db_table_create_statements import (
    CREATE_CITY_TABLE, CREATE_WEATHER_TABLE
)


def get_city_list():
    all_cities = dict()
    cities_list = []
    with open('initial_data/cities_list.csv', 'r') as csvfile:
        all_cities_list = csv.reader(csvfile)
        for city_name, lon, lat, _ in all_cities_list:
            all_cities[city_name] = (lon, lat)

    with open('initial_data/top_cities.csv', 'r') as csvfile:
        top_cities_list = csv.reader(csvfile)
        for (city_name,) in top_cities_list:
            lon, lat = all_cities[city_name]
            cities_list.append((city_name, lat, lon))
    return cities_list


async def main():
    start = datetime.now()
    connection = await asyncpg.connect(
        host=os.environ.get('DB_HOST'),
        port=os.environ.get('DB_PORT'),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD')
    )
    statements = [
        CREATE_CITY_TABLE,
        CREATE_WEATHER_TABLE,
    ]
    for statement in statements:
        await connection.execute(statement)
    for title, latitude, longitude in get_city_list():
        await connection.execute(
            """
            INSERT INTO city(city_id,title,latitude,longitude)
            VALUES(DEFAULT,$1,$2,$3)
            """,
            title, float(latitude), float(longitude))
    print('db_initial complete in', datetime.now()-start)
    await connection.close()


if __name__ == '__main__':
    asyncio.run(main())
