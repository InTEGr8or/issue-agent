from typing import List
from pydantic import BaseModel

# USV Delimiter
USV_DELIM = "\x1f"


class Issue(BaseModel):
    name: str  # The title or display name
    slug: str
    dependencies: List[str] = []
    # These are derived at runtime, not stored in USV
    priority: int = 0
    status: str = "unknown"

    def to_usv(self) -> str:
        deps_str = ",".join(self.dependencies)
        return f"{self.name}{USV_DELIM}{self.slug}{USV_DELIM}{deps_str}"
