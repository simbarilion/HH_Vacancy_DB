from src.hh_data_coordinator import HeadHunterDataCoordinator
from src.user_interaction import UserInteraction

# employer_id = {"Крок": "2987", "Точка банк": "2324020", "IBS": "139", "Aston": "6093775", "VK": "15478",
#                "Контур": "41862", "Тензор": "67611", "Лаборатория Касперского": "1057", "2ГИС": "64174",
#                "Skyeng": "1122462"}

EMPLOYER_ID: list[str] = ["2987", "2324020", "139", "6093775", "15478", "41862", "67611", "1057", "64174", "1122462"]
DB_NAME: str = "headhunter_vacancies"


def main() -> None:
    """ """
    try:
        user_interaction = UserInteraction()
        print(user_interaction.get_greeting())
        data_coordinator = HeadHunterDataCoordinator(EMPLOYER_ID, DB_NAME)
        data_coordinator.create_hh_database()
        while True:
            user_interaction.get_search_query()
            print(data_coordinator.execute_query(user_interaction.choice, user_interaction.key_word))

            if not user_interaction.is_restart():
                print(user_interaction.get_farewell())
                break
    except Exception:
        print("Не удалось загрузить данные. Попробуйте повторить позже")


if __name__ == "__main__":
    main()
