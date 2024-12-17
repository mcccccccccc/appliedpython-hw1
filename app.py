from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import tools
import plotly.graph_objects as go

from tools import ExceptionAPI


st.set_page_config(layout="wide")

st.title("Исторически температурный анализ")
'''
3. **Создание приложения на Streamlit**:
   - Добавить интерфейс для загрузки файла с историческими данными.
   - Добавить интерфейс для выбора города (из выпадающего списка).
   - Добавить форму для ввода API-ключа OpenWeatherMap. Когда он не введен, данные для текущей погоды не показываются. Если ключ некорректный, выведите на экран ошибку (должно приходить `{"cod":401, "message": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."}`).
   - Отобразить:
     - Описательную статистику по историческим данным для города, можно добавить визуализации.
     - Временной ряд температур с выделением аномалий (например, точками другого цвета).
     - Сезонные профили с указанием среднего и стандартного отклонения.
   - Вывести текущую температуру через API и указать, нормальна ли она для сезона.
'''
# Загрузка файла
uploaded_file = st.file_uploader("Выберете csv файл с данными", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    cities = df['city'].unique()

    city = st.selectbox("Выберете город (список тех что есть в файле)", cities)

    # API key
    api_key = st.text_input("Введите API key", type="password")

    if city and api_key:
        try:
            current_temp = tools.fetch_current_temperature(city, api_key)
        except ExceptionAPI as e:
            # остановка приложения если некорректный api_key
            st.error(e.err_body)
            st.stop()

        # statistics data
        city_data = df[df['city'] == city]
        df_stat = tools.seasonal_stats(df)
        df_anomaly = tools.detect_anomalies(df, df_stat)
        dr_roll = tools.rolling_mean_std(df)
        city_data_roll = dr_roll[dr_roll['city'] == city]
        anomalies = df_anomaly[df_anomaly['city'] == city]
        seasonal_profile = df_stat[df_stat['city'] == city]



        st.subheader(f"Статистика для {city}")

        st.write("df.describe")
        st.write(city_data.describe())

        st.write("Данные со скользящим средним и стандартным отклонением")
        st.write(city_data_roll)

        # Создание графиков

        fig = go.Figure()
        x = city_data_roll['timestamp']
        x_rev = x[::-1]
        y2 = city_data_roll['rolling_30_mean']
        y2_upper = city_data_roll['rolling_30_mean'] + city_data_roll['rolling_30_std']
        y2_lower = city_data_roll['rolling_30_mean'] - city_data_roll['rolling_30_std']
        y2_lower = y2_lower[::-1]
        fig.add_trace(go.Scatter(
            x=pd.concat([x, x_rev]),
            y=pd.concat([y2_upper, y2_lower]),
            fill='toself',
            fillcolor='rgba(0,176,246,0.2)',
            line_color='rgba(255,255,255,0)',
            name='std',
            showlegend=True,
        ))
        fig.add_trace(go.Scatter(
            x=x, y=y2,
            line_color='rgb(0,176,246)',
            name='Скользящее среднее 30 суток',
        ))
        anomalies_true = anomalies[anomalies['anomaly_temp'] == True]
        fig.add_trace(go.Scatter(
            x=anomalies_true['timestamp'],
            y=anomalies_true['temperature'],
            mode='markers',
            marker=dict(
                color='red',
                size=5,
                symbol='cross'
            ),
            name='Аномалии',
        ))
        st.plotly_chart(fig)


        st.subheader("Сезонные профили")

        st.write(seasonal_profile)

        x = seasonal_profile['season']
        x_rev = x[::-1]
        y2 = seasonal_profile['mean']
        y2_upper = seasonal_profile['mean'] + seasonal_profile['std']
        y2_lower = seasonal_profile['mean'] - seasonal_profile['std']
        y2_lower = y2_lower[::-1]
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
                        x=pd.concat([x, x_rev]),
                        y=pd.concat([y2_upper, y2_lower]),
                         fill='toself',
                         fillcolor='rgba(0,176,246,0.2)',
                         line_color='rgba(255,255,255,0)',
                         name='season std',
                         showlegend=True
        ))
        fig2.add_trace(go.Scatter(
            x=x,
            y=y2,
            line_color='rgb(0,176,246)',
            name='season mean',
            showlegend=True
        ))
        st.plotly_chart(fig2)

        # текущая тЕмпература
        if current_temp is not None:
            st.subheader("Текущая температура")
            month = datetime.now().month
            current_season = tools.month_to_season[month]
            stat = df_stat[(df_stat['city'] == city) & (df_stat['season'] == current_season)].iloc[0]
            up_level = stat['mean'] + 2 * stat['std']
            down_level = stat['mean'] - 2 * stat['std']
            is_anomaly_temp = current_temp > up_level or current_temp < down_level
            st.write(f"Текущая температура в городе {city}: {current_temp}°C")
            st.write(f"Является ли температура аномально: {'✅ - ДА' if is_anomaly_temp else '❌ - НЕТ'}")
