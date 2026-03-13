from dataclasses import dataclass, field
from typing import List, Optional

from .base import BaseIR


@dataclass
class ServiceIR(BaseIR):
    class_name: Optional[str] = None     # "UserService" (optional)
    function_name: str = ""              # "list_users"
    params: List[str] = field(default_factory=list)
    returns_type: Optional[str] = None   # "List[User]" etc.
    uses_model: Optional[str] = None     # "User"
