from .database import DatabaseManager
from .agent import OmniSQLAgent

# 明確定義包的對外接口
__all__ = ["DatabaseManager", "OmniSQLAgent"]

__version__ = "0.1.0"