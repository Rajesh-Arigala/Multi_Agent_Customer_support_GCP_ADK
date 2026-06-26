from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AgentResponse:
    status: str
    agent: str
    message: str
    data: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "agent": self.agent,
            "message": self.message,
            "data": self.data,
        }

