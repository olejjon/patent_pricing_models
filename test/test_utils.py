import psycopg2
import pytest

from util.utils import config, create_database


def test_existing_section():
    """Тест наличия данных для подключения"""
    params = config()

    assert "host" in params
    assert "port" in params
    assert "user" in params
    assert "password" in params


def test_empty_config_file(tmpdir):
    """Тест для случая, когда конфигурация файла существует, но он пустой"""
    empty_config_file = tmpdir.join("empty_database.ini")
    with open(empty_config_file, "w") as f:
        pass  # Создаем пустой файл
    with pytest.raises(Exception) as excinfo:
        config(empty_config_file, "postgresql")
    assert "Section postgresql is not found" in str(excinfo.value)


def test_non_existing_file():
    """Тест отсутствия файла"""

    with pytest.raises(Exception):
        config("non_existent.ini", "postgresql")


def test_create_database():
    """Тест создания базы"""
    db_params = {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': '123',
    }

    # Создаем соединение с базой данных postgres
    conn = psycopg2.connect(dbname='postgres', **db_params)
    conn.autocommit = True

    try:
        # Попытка создания базы данных 'job'
        create_database(db_params)
    except psycopg2.errors.DuplicateDatabase:
        pass

    # Проверяем, что база данных 'job' существует
    with conn.cursor() as cur:
        cur.execute("SELECT datname FROM pg_database WHERE datname = 'job'")
        result = cur.fetchone()

    assert result is not None, "База данных 'job' не существует"
