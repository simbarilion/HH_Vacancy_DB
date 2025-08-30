import os
from configparser import ConfigParser

from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(__file__)

LOGS_DIR = os.path.join(ROOT_DIR, "logs")

load_dotenv(os.path.join(ROOT_DIR, ".env"))


def config(filename: str = "database.ini", section: str = "postgresql") -> dict:
    """Возвращает параметры для подключения к БД"""
    parser = ConfigParser()
    parser.read(os.path.join(ROOT_DIR, filename), encoding="utf-8")

    if not parser.has_section(section):
        raise Exception(f"Section {section} is not found in the {filename} file")

    db_config = {key: value.strip() for key, value in parser.items(section)}

    db_config["user"] = os.getenv("DB_USER")
    db_config["password"] = os.getenv("DB_PASSWORD")

    return db_config
