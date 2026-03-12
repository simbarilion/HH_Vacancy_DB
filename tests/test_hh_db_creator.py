from unittest.mock import MagicMock, patch

import psycopg2
import pytest
from psycopg2 import sql

from src.database.hh_db_creator import HeadHunterDataBase


def test_enter_success(db):
    """Проверяет успешное соединение с базой данных"""
    mock_conn = MagicMock()
    with patch("psycopg2.connect", return_value=mock_conn):
        with db as data_base:
            assert data_base is db
            psycopg2.connect.assert_called_once()
            assert mock_conn.autocommit is False


def test_enter_fail(db):
    """Проверяет неуспешное соединение с базой данных"""
    with patch("psycopg2.connect", side_effect=psycopg2.Error()):
        with pytest.raises(psycopg2.Error):
            with db:
                pass


def test_create_database_new(db):
    """Проверяет успешное создание новой базы данных"""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = None

    with patch("psycopg2.connect", return_value=mock_conn):
        db.create_database()

    mock_cursor.execute.assert_any_call(
        "SELECT 1 FROM pg_database WHERE datname = %s", ("test_hh_db",)
    )
    mock_cursor.execute.assert_any_call(
        sql.SQL("CREATE DATABASE {}").format(sql.Identifier("test_hh_db"))
    )


def test_create_database_exists(db):
    """Проверяет успешное пересоздание базы данных"""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = (1,)

    with patch("psycopg2.connect", return_value=mock_conn):
        db.create_database()

    mock_cursor.execute.assert_any_call(
        sql.SQL("DROP DATABASE {}").format(sql.Identifier("test_hh_db"))
    )
    mock_cursor.execute.assert_any_call(
        sql.SQL("CREATE DATABASE {}").format(sql.Identifier("test_hh_db"))
    )


def test_create_database_error(db):
    """Проверяет неуспешное создание базы данных"""
    with patch("psycopg2.connect", side_effect=psycopg2.Error()):
        with pytest.raises(psycopg2.Error):
            db.create_database()
