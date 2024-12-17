# Сахаров Михаил Сергеевич ИИ-24

## ДЗ 1 (ОБЯЗАТЕЛЬНОЕ): Анализ температурных данных и мониторинг текущей температуры через OpenWeatherMap API

### Файлы
- [ИИ_ДЗ_1_(ОБЯЗАТЕЛЬНОЕ).ipynb](%D0%98%D0%98_%D0%94%D0%97_1_%28%D0%9E%D0%91%D0%AF%D0%97%D0%90%D0%A2%D0%95%D0%9B%D0%AC%D0%9D%D0%9E%D0%95%29.ipynb) - ноутбук с частю 1 и 2. Выводы и пояснения в комментариях в ячейках. 
- [app.py](app.py) - код для части 3 - Streamlit приложение
- [tools.py](tools.py) - вспомогательные функции для всех частей
- [temperature_data.csv](temperature_data.csv) - Cсгенерированный файл с данными с шумом. используется в части 2,3

## Приложение в облаке streamlit: 
https://appliedpython-hw1-mc.streamlit.app
- заморочился и сделал графики на plotly чтобы можно было потыкать поприближать
- делаю запрос в апи и получаю текущую температуру в выбранном городе
- можно выбрать город из списка или ввести свой
- на графике статистики красными точками отображаются температура в те жни когда зафиксирована аномалия
- обработал ошибку получения данных из апи через проброс ExceptionAPI. Это не самое элегантное решение но как демонстрация. 
