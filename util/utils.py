from configparser import ConfigParser

import pandas as pd
import psycopg2

from scr.DB import DB
from util.reference import reference


def work_with_user():
    """Функция для работы с пользователем"""

    params = config()

    try:
        db = DB('job', params)
    except psycopg2.OperationalError:
        print('Ошибка подключения к базе данных')
        print('Попробуем создать новую базу данных')
        try:
            create_database(params)
            print('Попробуйте перезапустить программу')
        except psycopg2.OperationalError:
            print("Проверьте БД")

    else:
        while True:
            print('Необходимо выбрать команду: \n'
                  '1. Прогнозирование цен средней цены.\n'
                  '2. Прогнозирование цен линейной регрессией.\n'
                  '3. Прогнозирование цен случайных деревьев.\n'
                  '4. Вывод информации о методах прогнозирования цен.\n'
                  '5. Пересоздание базы данных.\n'
                  '6. Новое заполнение даных из .cvs файла.\n'
                  '7. Выйти.\n')

            user_choice = input('Введите команду: ')
            if user_choice == '1':
                try:
                    db.load_data()
                    average_price = db.get_average_price_for_produt()
                    if average_price == {}:
                        print('Таблица данных пустая')
                    print('Средние цены:')
                    for key, value in average_price.items():
                        print(f'{key}:{value}')
                except psycopg2.errors.UndefinedTable:
                    print('Таблицы нет. Создайте ее!')
                except psycopg2.errors.InFailedSqlTransaction:
                    print('Ошибка - Создайте таблицу')

            elif user_choice == '2':
                try:
                    db.load_data()
                    db.train_model()
                    all_predict = db.predict_price_for_products()
                    if all_predict == {}:
                        print('Таблица данных пустая')
                    print('Цены спрогнозированные с помощью линейной регрессии:')
                    for key, value in all_predict.items():
                        mse = db.mse_calculation.get(key, None) / db.number
                        print(f'Прогнозируемая цена для {key}: {value},'
                              f'среднее отклонение {round((mse / value) * 100, 2)} процентов')
                except psycopg2.errors.UndefinedTable:
                    print('Таблицы нет. Создайте ее!')
                except psycopg2.errors.InFailedSqlTransaction:
                    print('Ошибка - Создайте таблицу')
            elif user_choice == '3':
                try:
                    db.load_data()
                    db.train_model_forest()
                    all_predict = db.predict_price_for_products()
                    if all_predict == {}:
                        print('Таблица данных пустая')
                    print('Цены спрогнозированные с помощью случайных деревьев:')
                    for key, value in all_predict.items():
                        mse = db.mse_calculation.get(key, None) / db.number_forest
                        print(f'Прогнозируемая цена для {key}: {value},'
                              f'среднее отклонение {round((mse / value) * 100, 2)} процентов')
                except psycopg2.errors.UndefinedTable:
                    print('Таблицы нет. Создайте ее!')
                except psycopg2.errors.InFailedSqlTransaction:
                    print('Ошибка - Создайте таблицу')
            elif user_choice == '4':
                print(reference)
            elif user_choice == '5':
                db.create_tables()
                print('База создана!')
            elif user_choice == '6':
                try:
                    csv_filename = "csv_data.csv"
                    df = pd.read_csv(csv_filename)
                except FileNotFoundError:
                    print("Нет файла для загрузки")
                else:
                    try:
                        db.error_table()
                    except psycopg2.errors.UndefinedTable:
                        # Проверка наличие таблицы
                        print("Нет таблиц, создайте - пункт 5")
                    else:
                        print("Таблица заполняется, подождите некоторое время")
                        print(f"Всего в базе {len(df)} элементов")
                        db.insert_table(csv_filename)
                        print("Таблицы заполнены")
            elif user_choice == '7':
                db.close_connection()
                print("Спасибо за использование\n" "Конец работы!")
                break


def create_database(params: dict):
    """Создание БД"""
    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("Create database job")
    cur.close()
    conn.close()


def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            "Section {0} is not found in the {1} file.".format(section, filename)
        )
    return db
