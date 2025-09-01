from src.hh_data_coordinator import HeadHunterDataCoordinator
from src.user_interaction import UserInteraction

# employer_id = {"Avito": "84585", "Точка банк": "2324020", "Купер": "1272486", "Aston": "6093775", "VK": "15478",
#                "Контур": "41862", "Тензор": "67611", "Яндекс": "1740", "2ГИС": "64174",
#                "Skyeng": "1122462"}

EMPLOYER_ID: list[str] = ["84585", "2324020", "1272486", "6093775", "15478",
                          "41862", "67611", "1740", "64174", "1122462"]
DB_NAME: str = "headhunter_vacancies"


def main() -> None:
    """Основная функция входа пользователя в программу"""
    data_coordinator = None
    try:
        user_interaction = UserInteraction()
        print(user_interaction.get_greeting())
        user_interaction.loading_output()
        data_coordinator = HeadHunterDataCoordinator(EMPLOYER_ID, DB_NAME)
        data_coordinator.create_hh_database()
        data_coordinator.create_db_manager_obj()
        while True:
            user_interaction.get_search_query()
            print(data_coordinator.execute_query(user_interaction.choice, user_interaction.key_word))

            if not user_interaction.is_restart():
                user_interaction.get_farewell()
                break
    except Exception as e:
        print(e)
        print("Не удалось загрузить данные. Попробуйте повторить позже")
    finally:
        if data_coordinator:
            data_coordinator.close_db_manager_obj_connection()


if __name__ == "__main__":
    main()
