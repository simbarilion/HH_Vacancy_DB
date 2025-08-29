class UserInteraction:
    """Класс для взаимодействия с пользователем"""
    def __init__(self):
        self.choice = 0
        self.key_word = None

    def get_greeting(self):
        """Возвращает приветствие в соотвествии с текущем временем суток"""
        return

    @staticmethod
    def get_farewell():
        """Возвращает 'До новых встреч' при завершении программы"""
        return "До новых встреч"

    def get_search_query(self):
        """Получает от пользователя выбор пункта меню"""
        choice = 0
        while choice not in range(1, 7):
            print(self.menu_output())
            choice = int(input(": "))
        self.choice = choice
        if choice == 5:
            self.get_key_word()
        if choice == 6:
            print(self.get_farewell())
            raise SystemExit()

    def get_key_word(self):
        """Получает от пользователя ключевое слово для запроса по ключевому слову"""
        key_word = input("Введите ключевое слово для поискового запроса: ")
        self.key_word = key_word

    @staticmethod
    def is_restart():
        """Получает от пользователя ответ, создать ли новый запрос"""
        restart = int(input("Сделать новую выборку? (да: 1, нет: 0): "))
        return restart == 1

    @staticmethod
    def menu_output():
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
