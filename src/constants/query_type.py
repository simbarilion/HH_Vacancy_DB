from enum import Enum


class QueryType(Enum):
    COMPANIES_VACANCIES_COUNT = 1
    ALL_VACANCIES = 2
    AVG_SALARY = 3
    HIGHER_SALARY = 4
    KEYWORD_SEARCH = 5
