"""table.py

    Chess table model.

"""
# Global package imports:
from pydantic import BaseModel, validator

# Local package imports:
from Organization.Models import ModelPlayer


class ModelTable(BaseModel):

    """Table data model."""

    number: int = 1
    w_player: ModelPlayer = 0
    b_player: ModelPlayer = 0
    result: float = -1.0

    @classmethod
    @validator('number')
    def number_match(cls, val):
        if not isinstance(val, int) or val <= 0:
            raise ValueError(f'Not valid table nr. ({val})')
        return val

    @classmethod
    @validator('w_player')
    def w_player_match(cls, val):
        if val != -1:
            if not isinstance(val, int) or val < 0:
                msg_error = f"Not valid white's id ({val})."
                raise ValueError(msg_error)
        return val

    @classmethod
    @validator('b_player')
    def b_player_match(cls, val):
        if val != -1:
            if not isinstance(val, int) or val < 0:
                msg_error = f"Not valid black's id ({val})."
                raise ValueError(msg_error)
        return val

    @classmethod
    @validator('result')
    def result_match(cls, val):
        _val = 0.0
        try:
            _val = float(val)
        except (FloatingPointError, ValueError) as exc:
            msg_error = f"Not result data ({val}). {exc}"
            raise ValueError(msg_error)
        if _val not in (-1.0, 0.0, 0.5, 1.0):
            msg_error = f"Wrong result value ({val})."
            raise ValueError(msg_error)
        return _val
