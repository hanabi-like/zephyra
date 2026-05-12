from __future__ import annotations

from typing import Any

from zephyra.validation.tool_invoke import validate_tool_invoke
from zephyra.tools.base import ToolAdapter
from zephyra.tools.models import ToolDescriptor, ToolError, ToolResult


class ToolExecutor:
    def __init__(self, adapter: ToolAdapter) -> None:
        self.adapter = adapter
        self._tools_by_name: dict[str, ToolDescriptor] = {}

    def load_tools(self) -> list[ToolDescriptor]:
        tools = self.adapter.list_tools()
        self._tools_by_name = {tool.name: tool for tool in tools}
        return tools

    def list_tools(self) -> list[ToolDescriptor]:
        if not self._tools_by_name:
            return self.load_tools()

        return list(self._tools_by_name.values())

    def execute(
        self,
        tool_name: str,
        args: dict[str, Any],
    ) -> ToolResult:
        if not self._tools_by_name:
            self.load_tools()

        descriptor = self._tools_by_name.get(tool_name)
        if descriptor is None:
            return ToolResult(
                ok=False,
                tool_name=tool_name,
                error=ToolError(
                    code="tool_not_found", message=f"unknown tool: {tool_name}"
                ),
            )

        validation_errors = validate_tool_invoke(tool_name, args, descriptor)
        if validation_errors:
            return ToolResult(
                ok=False,
                tool_name=tool_name,
                error=ToolError(
                    code="invalid_arguments", message="; ".join(validation_errors)
                ),
            )

        return self.adapter.invoke(
            tool_name=tool_name,
            args=args,
        )
