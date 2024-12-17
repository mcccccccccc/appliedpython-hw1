from datetime import datetime

import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import tools
import plotly.graph_objects as go


# Streamlit UI
st.title("Temperature Data Analysis and Monitoring")

# File upload
uploaded_file = st.file_uploader("Upload historical temperature data", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['season'] = df['timestamp'].dt.month.map(lambda x: {12: "winter", 1: "winter", 2: "winter",
                                                           3: "spring", 4: "spring", 5: "spring",
                                                           6: "summer", 7: "summer", 8: "summer",
                                                           9: "autumn", 10: "autumn", 11: "autumn"}[x])
    cities = df['city'].unique()

    # City selection
    city = st.selectbox("Select a city", cities)

    # API key input
    api_key = st.text_input("Enter OpenWeatherMap API key", type="password")

    if city and api_key:
        # Display historical data statistics
        st.subheader(f"Historical Data Statistics for {city}")
        city_data = df[df['city'] == city]
        st.write(city_data.describe())

        # Calculate seasonal statistics and detect anomalies
        df_stat = tools.seasonal_stats(df)
        df_anomaly = tools.detect_anomalies(df, df_stat)
        dr_roll = tools.rolling_mean_std(df)
        city_data_roll = dr_roll[dr_roll['city'] == city]
        anomalies = df_anomaly[df_anomaly['city'] == city]

        # Plot temperature time series with anomalies using Plotly
        # st.subheader("Temperature Time Series with Anomalies")

        # fig = px.line(city_data_roll, x='timestamp', y='rolling_30_mean', title='Rolling mean temperature Time Series with Anomalies')
        # fig.add_trace(go.Scatter(x='timestamp', y='temperature', mode='lines+markers', name='Temperature'))
        # fig.add_scatter(x=anomalies['timestamp'], y=anomalies['temperature'], mode='markers', name='Anomalies', marker=dict(color='red'))
        # st.plotly_chart(fig)

        # Создание графиков
        fig = go.Figure()

        # Первый график
        fig.add_trace(go.Scatter(x=city_data_roll['timestamp'], y=city_data_roll['rolling_30_mean'], mode='lines', name='График 1'))

        # Второй график
        fig.add_trace(go.Scatter(x=city_data['timestamp'], y=city_data['temperature'], mode='markers', name='График 2'))
        st.plotly_chart(fig)

        # Plot seasonal profiles
        st.subheader("Seasonal Profiles")
        seasonal_profile = df_stat[df_stat['city'] == city]
        fig = px.scatter(seasonal_profile, x='season', y='mean', error_y='std', title='Seasonal Profiles')
        st.plotly_chart(fig)

        # Fetch and display current temperature
        current_temp = tools.fetch_current_temperature(city, api_key)
        if current_temp is not None:
            st.subheader("Current Temperature")
            st.write(f"The current temperature in {city} is {current_temp}°C.")

            # Check if current temperature is an anomaly
            month = datetime.now().month
            current_season = tools.month_to_season[month]
            stat = df_stat[(df_stat['city'] == city) & (df_stat['season'] == current_season)].iloc[0]
            up_level = stat['mean'] + 2 * stat['std']
            down_level = stat['mean'] - 2 * stat['std']
            is_anomaly_temp = current_temp > up_level or current_temp < down_level
            st.write(f"Is the current temperature an anomaly? {'Yes' if is_anomaly_temp else 'No'}")