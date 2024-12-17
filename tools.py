import pandas as pd
import numpy as np
import requests
import aiohttp

month_to_season = {12: "winter", 1: "winter", 2: "winter",
                   3: "spring", 4: "spring", 5: "spring",
                   6: "summer", 7: "summer", 8: "summer",
                   9: "autumn", 10: "autumn", 11: "autumn"}

# Вычисление скользящего среднего и стандартного отклонения для сглаживания температурных колебаний.
def rolling_mean_std(df):
    df.loc[:,['rolling_30_mean']] = df.groupby('city')['temperature'].transform(lambda x: x.rolling(window=30).mean())
    df.loc[:,['rolling_30_std']] = df.groupby('city')['temperature'].transform(lambda x: x.rolling(window=30).std())

    return df


# Определение аномалий на основе отклонений температуры от $ \text{скользящее среднее} \pm 2\sigma $.
def detect_anomalies(df, df_stat):
    # print(df_stat.columns)
    df = df.merge(df_stat, on=['city', 'season'])
    # print(df)
    up_level = df['mean'] + 2 * df['std']
    down_level = df['mean'] - 2 * df['std']
    df['anomaly_temp'] = (df['temperature'] > up_level) | (df['temperature'] < down_level)

    return df


# Рассчитать среднюю температуру и стандартное отклонение для каждого сезона в каждом городе.
def seasonal_stats(df):
    df_group = df.groupby(['city', 'season'])['temperature'].agg(['mean', 'std']).reset_index()

    return df_group


async def fetch_async(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


def fetch_sync(url):
    response = requests.get(url)
    return response.json()


def check_anomaly(df_stat, city, current_temp):
    stat = df_stat[(df_stat['city'] == city) & (df_stat['season'] == month_to_season[12])].to_dict(orient='records')[0]
    up_level = stat['mean'] + 2 * stat['std']
    down_level = stat['mean'] - 2 * stat['std']
    is_anomaly_temp = current_temp > up_level or current_temp < down_level

    return is_anomaly_temp

def fetch_current_temperature(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = fetch_sync(url)
    current_temp = response['main']['temp'] if 'main' in response else None
    return current_temp


