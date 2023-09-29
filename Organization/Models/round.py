"""round.py

    Round model.

"""
# Global package imports:
from typing import Union, Dict, Optional
from pydantic import BaseModel, validator

# Local package imports:


class ModelRound(BaseModel):
    """Turnament round model."""

    number: Optional[int] = 0
    tables: Optional[Dict] = {}
    pausing: Optional[Union[int, bool]] = 0
    all_results: Optional[bool] = False
    players_qty: Optional[int] = 0
    tables_qty: Optional[int] = 0

    @validator('number')
    def number_match(cls, val):
        if not isinstance(val, int) and val < 0:
            raise ValueError(f'Round number wrong. ({val})')
        return val

    @validator('players_qty')
    def players_num_match(cls, val):
        if not isinstance(val, int) and val < 0:
            raise ValueError(f'Players quantity wrong. ({val})')
        return val
    
    @validator('tables_qty')
    def tables_num_match(cls, val):
        if not isinstance(val, int) and val < 0:
            raise ValueError(f'Tables quantity wrong. ({val})')
        return val
