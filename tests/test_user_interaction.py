from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time

from src.user_interaction import UserInteraction


def test_get_search_query_valid_3(user_interaction: UserInteraction) -> None:
    """Проверяет выбор пользователем пункта меню 3"""
    user_interaction._output_menu = MagicMock(return_value="menu")
    user_interaction._get_key_word = MagicMock()
    user_interaction.get_farewell = MagicMock()

    with patch("builtins.input", side_effect="3"):
        user_interaction.get_search_query()

    assert user_interaction.choice == 3
    user_interaction._output_menu.assert_called_once()
    user_interaction._get_key_word.assert_not_called()
    user_interaction.get_farewell.assert_not_called()


def test_get_search_query_valid_5(user_interaction: UserInteraction) -> None:
    """Проверяет выбор пользователем пункта меню 5"""
    user_interaction._output_menu = MagicMock(return_value="menu")
    user_interaction._get_key_word = MagicMock()
    user_interaction.get_farewell = MagicMock()

    with patch("builtins.input", side_effect="5"):
        user_interaction.get_search_query()

    assert user_interaction.choice == 5
    user_interaction._output_menu.assert_called_once()
    user_interaction._get_key_word.assert_called_once()
    user_interaction.get_farewell.assert_not_called()


def test_get_search_query_valid_6(user_interaction: UserInteraction) -> None:
    """Проверяет выбор пользователем пункта меню 6"""
    user_interaction._output_menu = MagicMock(return_value="menu")
    user_interaction._get_key_word = MagicMock()
    user_interaction.get_farewell = MagicMock()

    with patch("builtins.input", side_effect="6"):
        with pytest.raises(SystemExit):
            user_interaction.get_search_query()

    assert user_interaction.choice == 0
    user_interaction._output_menu.assert_called_once()
    user_interaction._get_key_word.assert_not_called()
    user_interaction.get_farewell.assert_called_once()


@freeze_time("2025-09-03 08:00:00")
def test_get_greeting_morning(user_interaction: UserInteraction) -> None:
    """Проверяет корректное приветствие в зависимости от текущего времени: утро"""
    assert user_interaction.get_greeting() == "Доброе утро!"


@freeze_time("2025-09-03 12:30:00")
def test_get_greeting_afternoon(user_interaction: UserInteraction) -> None:
    """Проверяет корректное приветствие в зависимости от текущего времени: день"""
    assert user_interaction.get_greeting() == "Добрый день!"


@freeze_time("2025-09-03 18:00:10")
def test_get_greeting_evening(user_interaction: UserInteraction) -> None:
    """Проверяет корректное приветствие в зависимости от текущего времени: вечер"""
    assert user_interaction.get_greeting() == "Добрый вечер!"


@freeze_time("2025-09-03 00:05:00")
def test_get_greeting_night(user_interaction: UserInteraction) -> None:
    """Проверяет корректное приветствие в зависимости от текущего времени: ночь"""
    assert user_interaction.get_greeting() == "Доброй ночи!"
