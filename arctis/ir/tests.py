from dataclasses import dataclass
from typing import Optional

from .base import BaseIR


@dataclass
class TestIR(BaseIR):
    function_name: str                   # "test_get_users"
    targets_route: Optional[str] = None  # "get_users"
