import os
from configparser import ConfigParser

ROOT_DIR = os.path.dirname(__file__)

DATA_DIR = os.path.join(ROOT_DIR, "data")

LOGS_DIR = os.path.join(ROOT_DIR, "logs")


def config(filename: str = "database.ini", section: str = "postgresql") -> dict:
    """Возвращает параметры для подключения к БД"""
    parser = ConfigParser()

    parser.read(os.path.join(ROOT_DIR, filename), encoding='utf-8')

    if not parser.has_section(section):
        raise Exception(f"Section {section} is not found in the {filename} file")

    return {key: value.strip() for key, value in parser.items(section)}
