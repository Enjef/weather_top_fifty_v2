CREATE_DATABASE_WEATHER = 'CREATE DATABASE postgres;'

CREATE_CITY_TABLE = \
    '''
    CREATE TABLE IF NOT EXISTS city (
        city_id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        latitude FLOAT NOT NULL,
        longitude FLOAT NOT NULL
    );'''

CREATE_WEATHER_TABLE = \
    '''
    CREATE TABLE IF NOT EXISTS weather(
        id SERIAL PRIMARY KEY,
        city_id INT NOT NULL,
        cur_temp FLOAT NOT NULL,
        humidity INT NOT NULL,
        pressure INT NOT NULL,
        description TEXT NOT NULL,
        wind_speed FLOAT NOT NULL,
        date TIMESTAMP NOT NULL,
        timezone_shift INT NOT NULL,
        FOREIGN KEY (city_id)
        REFERENCES city(city_id)
    );'''
