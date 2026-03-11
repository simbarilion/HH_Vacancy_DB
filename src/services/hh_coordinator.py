from typing import Optional

from src.api.hh_api_service import HeadHunterAPI
from src.database.hh_db_service import HeadHunterDBCreator, HeadHunterDBManager


class HeadHunterDataCoordinator:
    """
    Связывает API, DB Creator и DB Manager, отвечает за workflow:
    получение данных, создание/заполнение БД, выполнение запросов
    """

    def __init__(self, employers_id: list[str], db_name: str):
        """Конструктор класса HeadHunterDataCoordinator"""
        self.api = HeadHunterAPI(employers_id)
        self.db_creator = HeadHunterDBCreator(db_name)
        self.db_manager: Optional[HeadHunterDBManager] = None

    def connect_db(self):
        if not self.db_manager:
            raise RuntimeError("DB Manager not initialized")
        self.db_manager.open_connection()

    def setup_database(self):
        companies = self.api.get_companies()
        vacancies = self.api.get_vacancies()
        self.db_creator.create_and_fill_db(companies, vacancies)
        self.db_manager = HeadHunterDBManager(self.db_creator.db_name)
        self.connect_db()

    def query(self, query_id: int, key_word: str = "") -> str:
        if not self.db_manager:
            raise RuntimeError("DB Manager not initialized")
        return self.db_manager.execute_query(query_id, key_word)

    def close(self) -> None:
        """Закрывает соединение с базой данных"""
        if self.db_manager:
            self.db_manager.close_connection()
