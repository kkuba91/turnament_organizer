"""player.py

    Chess player model.

"""
# Global package imports:
from datetime import date
from typing import Union, List, Any
from pydantic import BaseModel, ValidationError, validator

# Local package imports:
from resources import CATEGORY


class ModelPlayer(BaseModel):
    """Chess Player class model."""
    # Static data:
    name: str
    surname: str
    sex: str
    birth_date: Union[date, str, None] = None
    city: str = ""
    category: str = "bk"
    elo: int = 0
    rank: int = 0
    club: str = ""

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

    @validator('sex')
    def sex_for_category_match(cls, val):
        _genders = [_genders for _genders, _ in CATEGORY.items()]
        if val not in _genders:
            raise ValueError(f'Not valid gender name. ({val})')
        return val

    @validator('category')
    def category_match(cls, val):
        male_cats = [_cats for _cats, _ in CATEGORY['male'].items()]
        female_cats = [_cats for _cats, _ in CATEGORY['female'].items()]
        if val not in male_cats or val not in female_cats:
            msg_error = f'Not valid category name ({val}).'
            raise ValueError(msg_error)
        return val
