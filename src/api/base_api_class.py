import threading
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
        self.local = threading.local()

    def _get_session(self) -> requests.Session:
        """Создаёт session отдельно для каждого потока"""
        if not hasattr(self.local, "session"):
            session = requests.Session()

            retry = Retry(
                total=3,  # максимум 3 попытки
                backoff_factor=1,  # задержка между повторами
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET"],
            )
            adapter = HTTPAdapter(  # определяет политику повторных попыток
                max_retries=retry,
                pool_connections=10,
                pool_maxsize=10
            )

            session.mount("https://", adapter)
            session.mount("http://", adapter)

            self.local.session = session

        return self.local.session

    def _get_response(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None) -> Optional[dict]:
        """Выполняет GET запрос и возвращает JSON"""
        session = self._get_session()
        try:
            response = session.get(url, headers=headers, params=params, timeout=(3, 10))  # timeout на connect, read
            response.raise_for_status()
            result = response.json()
            self.logger.debug("JSON получен")
            return result
        except requests.exceptions.Timeout as err:
            self.logger.error(f"Ошибка таймаута: {err}")
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Ошибка запроса: {err}")
        except JSONDecodeError as err:
            self.logger.error(f"Ошибка декодирования JSON: {err}")
        return None

    @abstractmethod
    def get_formatted_data(self) -> list[dict]:
        """Возвращает список моделей данных"""
        pass
