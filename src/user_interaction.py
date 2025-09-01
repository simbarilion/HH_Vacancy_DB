from datetime import datetime
from typing import Optional


class UserInteraction:
    """Класс для взаимодействия с пользователем"""
    def __init__(self) -> None:
        self.choice: int = 0
        self.key_word: Optional[str] = None

    def get_search_query(self) -> None:
        """Получает от пользователя выбор пункта меню"""
        choice = 0
        while choice not in range(1, 7):
            print(self.output_menu())
            try:
                choice = int(input("(Введите число от 1 до 6)\n: "))
            except ValueError:
                print("Введено некорректное значение")
                continue
            if choice == 5:
                self.get_key_word()
            if choice == 6:
                self.get_farewell()
                raise SystemExit()
            self.choice = choice

    def get_key_word(self) -> None:
        """Получает от пользователя ключевое слово для запроса по ключевому слову"""
        key_word = input("Введите ключевое слово для поискового запроса: ")
        self.key_word = key_word

    @staticmethod
    def get_greeting() -> str:
        """Возвращает приветствие в зависимости от текущего времени"""
        date_obj = datetime.now()
        if 6 <= date_obj.hour < 12:
            return "Доброе утро!"
        elif 12 <= date_obj.hour < 18:
            return "Добрый день!"
        elif 18 <= date_obj.hour < 24:
            return "Добрый вечер!"
        else:
            return "Доброй ночи!"

    @staticmethod
    def loading_output() -> None:
        """Выводит сообщение о процессе загрузки данных"""
        print("Идет загрузка данных ...")

    @staticmethod
    def get_farewell() -> None:
        """Выводит сообщение при завершении программы"""
        print("До новых встреч!")

    @staticmethod
    def output_menu() -> str:
        """Возвращает основное меню программы"""
        return """
                Пожалуйста, выберите пункт меню:
                1. Список компаний и количество вакансий 
                2. Информация обо всех вакансиях
                3. Средняя зарплата по вакансиям у каждой компании
                4. Список вакансий с зарплатой выше средней
                5. Список вакансий по ключевому слову в названии
                6. Выйти из программы
                """

    @staticmethod
    def is_restart() -> bool:
        """Получает от пользователя ответ, создать ли новый запрос"""
        while True:
            try:
                restart = int(input("Сделать новую выборку? (да: 1, нет: 0): "))
                return restart == 1
            except ValueError:
                print("Введите 1 или 0")
