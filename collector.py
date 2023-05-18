import asyncio
import logging
import os
from datetime import datetime

import asyncpg
from aiohttp import ClientSession


logging.basicConfig(
    filename='weather_db_logs/weather_collector.log',
    level=logging.ERROR,
    format='%(asctime)s:%(levelname)s:%(message)s'
)


async def insert_current_weather(data, connection):
    city_id = data['city_id']
    wind = float(data.get('wind', {'speed': 0})['speed'])
    cur_temp = data['main']['temp']
    humidity = data['main']['humidity']
    pressure = data['main']['pressure']
    weather_description = data['weather'][0]['main']
    timezone_shift = data['timezone']
    date = datetime.fromtimestamp(data['dt'])
    await connection.execute(
        """
        INSERT INTO weather(
            id,city_id,cur_temp,humidity,pressure,description,
            wind_speed,date,timezone_shift
        )
        VALUES(DEFAULT,$1,$2,$3,$4,$5,$6,$7,$8)
        """,
        city_id, cur_temp, humidity, pressure, weather_description,
        wind, date, timezone_shift
    )


async def api_current_weather(city, api_key, session):
    city_id = city.get('city_id')
    lat = city.get('latitude')
    lon = city.get('longitude')
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric'
    async with session.get(url) as response:
        data = await response.json()
    data.update({'city_id': city_id})
    return data


class Collector:
    def __init__(self, api_key, api_get, data_insert) -> None:
        self.api_key = api_key
        self.api_get = api_get
        self.data_insert = data_insert

    async def collect(self):
        connection = await asyncpg.connect(
            host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT'),
            database=os.environ.get('DB_NAME'),
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD')
        )
        session = ClientSession()
        cities = await connection.fetch(
            'SELECT * FROM city;'
        )
        while True:
            start = datetime.now()
            request_tasks = []
            for city in cities:
                request_tasks.append(
                    self.api_get(city, self.api_key, session))
            try:
                for task in asyncio.as_completed(request_tasks, timeout=10):
                    data = await task
                    await self.data_insert(data, connection)
            except KeyboardInterrupt:
                await session.close()
                await connection.close()
                asyncio.get_event_loop().close()
                break
            except asyncio.TimeoutError as ex:
                logging.exception(f'Не удалось получить данные: {ex}')
                break
            except Exception as ex:
                logging.exception(f'Не удалось сохранить данные: {ex}')
            print('Collection done in', datetime.now()-start)
            await asyncio.sleep(70)
        return


async def main():
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    weather_collector = Collector(
        api_key, api_current_weather, insert_current_weather)
    await weather_collector.collect()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
