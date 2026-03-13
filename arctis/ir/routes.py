from dataclasses import dataclass, field
from typing import List, Optional

from .base import BaseIR


@dataclass
class RouteIR(BaseIR):
    function_name: str
    http_method: str          # "GET", "POST", ...
    path: str                 # "/users", "/users/<id>"
    decorators: List[str] = field(default_factory=list)
    uses_service: Optional[str] = None   # "UserService" oder "user_service.list_users"
    returns_type: Optional[str] = None   # "JSON", "HTML", "Response"
