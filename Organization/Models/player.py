"""player.py

    Chess player model.

"""
# Global package imports:
from datetime import date
from typing import Union, List, Any
from pydantic import BaseModel, validator

# Local package imports:
from resources import CATEGORY


class ModelPlayer(BaseModel):
    """Chess Player class model."""
    # Static data:
    name: str = ""
    surname: str = ""
    sex: str = ""
    birth_date: Union[date, str, None] = None
    city: str = ""
    category: str = "bk"
    elo: int = 0
    rank: int = 0
    club: str = ""

    # Feature:
    pauser: bool = False

    # Dynamic data:
    place: int = 0
    id: int = 0
    paused: bool = False
    points: float = 0.0
    progress: float = 0.0
    bucholz: float = 0.0
    achieved_rank: float = 0.0
    last_played_white: bool = False
    rounds: Union[None, Any] = None
    opponents: List[int] = []
    possible_opponents: List[int] = []
    results: List[int] = []
    round_done: bool = False

    @validator('name')
    def name_any_match(cls, name, values):
        pauser = values.get('pauser')
        if len(name) == 0 and not pauser:
            raise ValueError(f'No name. ({name})')
        return name

    @validator('surname')
    def surname_any_match(cls, surname, values):
        pauser = values.get('pauser')
        if len(surname) == 0 and not pauser:
            raise ValueError(f'No surname. ({surname})')
        return surname

    @validator('sex')
    def sex_for_category_match(cls, sex, values):
        pauser = values.get('pauser')
        _genders = [_genders for _genders, _ in CATEGORY.items()]
        if sex not in _genders and not pauser:
            raise ValueError(f'Not valid gender name. ({sex})')
        return sex

    @validator('category')
    def category_match(cls, category, values):
        pauser = values.get('pauser')
        male_cats = [_cats for _cats, _ in CATEGORY['male'].items()]
        female_cats = [_cats for _cats, _ in CATEGORY['female'].items()]
        if not pauser:
            if category not in male_cats or category not in female_cats:
                msg_error = f'Not valid category name ({category}).'
                raise ValueError(msg_error)
        return category
