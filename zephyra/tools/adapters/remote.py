from __future__ import annotations

from typing import Any

import requests

from zephyra.tools.base import ToolAdapter
from zephyra.tools.models import (
    ToolProperty,
    ToolSchema,
    ToolDescriptor,
    ToolError,
    ToolResult,
)


class RemoteToolAdapter(ToolAdapter):
    def __init__(self, gateway_base_url: str, timeout_seconds: float = 10.0) -> None:
        self.gateway_base_url = gateway_base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def list_tools(self) -> list[ToolDescriptor]:
        url = f"{self.gateway_base_url}/tools"

        response = requests.get(url=url, timeout=self.timeout_seconds)
        response.raise_for_status()

        body = response.json()
        if not isinstance(body, list):
            raise ValueError(
                f"invalid tool list response: expected list, got {type(body).__name__}"
            )

        return [self._parse_tool_descriptor(item) for item in body]

    def invoke(
        self,
        tool_name: str,
        args: dict[str, Any],
    ) -> ToolResult:
        url = f"{self.gateway_base_url}/tools/invoke"

        payload = {
            "tool_name": tool_name,
            "args": args,
        }

        try:
            response = requests.post(
                url=url, json=payload, timeout=self.timeout_seconds
            )
            response.raise_for_status()

            body = response.json()
        except requests.Timeout:
            return ToolResult(
                ok=False,
                tool_name=tool_name,
                error=ToolError(
                    code="tool_timeout",
                    message=f"tool '{tool_name}' invocation timed out after {self.timeout_seconds} seconds",
                ),
            )
        except requests.RequestException as e:
            return ToolResult(
                ok=False,
                tool_name=tool_name,
                error=ToolError(
                    code="tool_gateway_failed",
                    message=f"tool '{tool_name}' invocation failed through gateway: {e}",
                ),
            )

        if not isinstance(body, dict):
            return ToolResult(
                ok=False,
                tool_name=tool_name,
                error=ToolError(
                    code="invalid_tool_invoke_response",
                    message=f"expected dict, got {type(body).__name__}",
                ),
            )

        return self._parse_tool_result(body)

    def _parse_tool_schema(self, body: dict[str, Any]) -> ToolSchema:
        properties = {
            key: ToolProperty(type=value["type"], description=value.get("description"))
            for key, value in body.get("properties", {}).items()
        }

        return ToolSchema(
            type=body.get("type", "object"),
            properties=properties,
            required=body.get("required", []),
        )

    def _parse_tool_descriptor(self, body: dict[str, Any]) -> ToolDescriptor:
        return ToolDescriptor(
            name=body["name"],
            description=body["description"],
            input_schema=self._parse_tool_schema(body["input_schema"]),
            output_schema=(
                None
                if body.get("output_schema") is None
                else self._parse_tool_schema(body["output_schema"])
            ),
            timeout_seconds=body.get("timeout_seconds"),
            tags=body.get("tags", []),
        )

    def _parse_tool_result(self, body: dict[str, Any]) -> ToolResult:
        error = body.get("error")

        return ToolResult(
            ok=body["ok"],
            tool_name=body["tool_name"],
            data=body.get("data"),
            error=(
                None
                if error is None
                else ToolError(code=error["code"], message=error["message"])
            ),
        )
