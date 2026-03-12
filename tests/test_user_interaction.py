from freezegun import freeze_time


@freeze_time("2025-09-03 08:00:00")
def test_get_greeting_morning(user_interaction):
    """Проверяет корректное приветствие в зависимости от текущего времени: утро"""
    assert user_interaction.get_greeting() == "Доброе утро!"


@freeze_time("2025-09-03 12:30:00")
def test_get_greeting_afternoon(user_interaction):
    """Проверяет корректное приветствие в зависимости от текущего времени: день"""
    assert user_interaction.get_greeting() == "Добрый день!"


@freeze_time("2025-09-03 18:00:10")
def test_get_greeting_evening(user_interaction):
    """Проверяет корректное приветствие в зависимости от текущего времени: вечер"""
    assert user_interaction.get_greeting() == "Добрый вечер!"


@freeze_time("2025-09-03 00:05:00")
def test_get_greeting_night(user_interaction):
    """Проверяет корректное приветствие в зависимости от текущего времени: ночь"""
    assert user_interaction.get_greeting() == "Доброй ночи!"
