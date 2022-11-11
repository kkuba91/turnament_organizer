"""table.py

    Chess table model.

"""
# Global package imports:
from pydantic import BaseModel, validator

# Local package imports:


class ModelTable(BaseModel):

    """Table data model."""

    number: int = 1
    w_player: int = 0
    b_player: int = 0
    result: float = -1.0


    @validator('number')
    def number_match(cls, val):
        if not isinstance(val, int) or val <= 0:
            raise ValueError(f'Not valid table nr. ({val})')
        return val

    @validator('w_player')
    def w_player_match(cls, val):
        if not isinstance(val, int) or val < 0:
            msg_error = f"Not valid white's id ({val})."
            raise ValueError(msg_error)
        return val

    @validator('b_player')
    def b_player_match(cls, val):
        if not isinstance(val, int) or val < 0:
            msg_error = f"Not valid black's id ({val})."
            raise ValueError(msg_error)
        return val

    @validator('result')
    def result_match(cls, val):
        _val = 0.0
        try:
            _val = float(val)
        except (FloatingPointError, ValueError) as exc:
            msg_error = f"Not result data ({val})."
            raise ValueError(msg_error)
        if _val not in (-1.0, 0.0, 0.5, 1.0):
            msg_error = f"Wrong result value ({val})."
            raise ValueError(msg_error)
        return _val
