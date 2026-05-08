from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from zephyra.tools.models import ToolDescriptor, ToolResult


class ToolAdapter(ABC):
    @abstractmethod
    def list_tools(self) -> list[ToolDescriptor]:
        raise NotImplementedError

    @abstractmethod
    def invoke(
        self,
        tool_name: str,
        args: dict[str, Any],
    ) -> ToolResult:
        raise NotImplementedError
