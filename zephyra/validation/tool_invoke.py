from __future__ import annotations

from typing import Any

from zephyra.tools.models import ToolDescriptor

TYPE_MAPPING = {
    "string": str,
}


def validate_tool_invoke(
    tool_name: str,
    args: dict[str, Any],
    descriptor: ToolDescriptor,
) -> list[str]:
    errors: list[str] = []

    errors.extend(_validate_tool_name(tool_name, descriptor))
    errors.extend(_validate_args(args, descriptor))

    return errors


def _validate_tool_name(tool_name: str, descriptor: ToolDescriptor) -> list[str]:
    if not isinstance(tool_name, str):
        return [f"tool_name: expected string, got {type(tool_name).__name__}"]

    if not tool_name:
        return ["tool_name: expected non-empty, got empty"]

    if tool_name != descriptor.name:
        return [f"tool_name: expected {descriptor.name}, got {tool_name}"]

    return []


def _validate_args(args: dict[str, Any], descriptor: ToolDescriptor) -> list[str]:
    if not isinstance(args, dict):
        return [f"args: expected object, got {type(args).__name__}"]

    errors: list[str] = []

    schema = descriptor.input_schema

    for key in schema.required:
        if key not in args:
            errors.append(f"args.{key}: missing required property")

    for key, value in args.items():
        if not isinstance(key, str):
            errors.append(f"args.{key}: expected string, got {type(key).__name__}")
            continue

        if not key:
            errors.append(f"args.{key}: expected non-empty, got empty")
            continue

        if key not in schema.properties:
            errors.append(f"args.{key}: unexpected property")
            continue

        expected_value = schema.properties.get(key)

        expected_type = TYPE_MAPPING.get(expected_value.type)

        if expected_type is None:
            errors.append(f"args.{key}: unsupported type {expected_value.type}")
            continue

        if not isinstance(value, expected_type):
            errors.append(
                f"args.{key}: expected {expected_value.type}, got {type(value).__name__}"
            )
            continue

    return errors
