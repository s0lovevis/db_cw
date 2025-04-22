# db_cw
Курсовая работа по предмету Специальные главы по БД на тему "SRM система мебельного магазина для работы с поставщиками"

## для запуска:

В корневой директории создаем файлик .env с переменными:
```
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

REDIS_HOST=
REDIS_PORT=
REDIS_PASSWORD=

MONGO_USER=
MONGO_PASSWORD=
MONGO_HOST=
MONGO_PORT=
MONGO_AUTH_DB=
```

Запуск программы производится командой:
```
streamlit run app.py  
```
При самом первом использовании программы(или для полного сброса всех данных) необходимо вызвать init_script:
```
./init_script
```
