from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from src.logging_config import LoggingConfigClassMixin


class BaseAPISource(ABC, LoggingConfigClassMixin):
    """Базовый класс для работы с API"""

    def __init__(self) -> None:
        super().__init__()
        self.logger = self.configure()
        self.session = requests.Session()

        retry = Retry(
            total=3,  # максимум 3 попытки
            backoff_factor=1,  # задержка между повторами
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry)  # определяет политику повторных попыток
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        self.logger.info("HTTP session закрыта")

    def _get_response(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None) -> Optional[dict]:
        """Выполняет GET запрос и возвращает JSON"""
        try:
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            self.logger.info("Данные преобразованы в json-формат")
            return result
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Ошибка запроса: {err}")
        except JSONDecodeError as err:
            self.logger.error(f"Ошибка декодирования JSON: {err}")
        return None

    @abstractmethod
    def get_formatted_data(self) -> list[dict]:
        """Возвращает список моделей данных"""
        pass
