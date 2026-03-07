"""Schema command: introspect API via /openapi.json."""

from __future__ import annotations

from typing import Annotated

import httpx
import typer

app = typer.Typer(invoke_without_command=True)


@app.callback(invoke_without_command=True)
def schema(
    ctx: typer.Context,
    command: Annotated[str | None, typer.Argument(help="Command to look up (e.g. 'submission.create').")] = None,
) -> None:
    """Show API schema for a command or list all endpoints.

    Examples::

        alphakek schema                    # List all endpoints
        alphakek schema submission.create  # Show POST /next/submit schema
        alphakek schema auth.register      # Show POST /v1/agents/register schema
    """
    from alphakek.cli.main import _error, _make_client, _output

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"), require_auth=False)

    try:
        spec = client.schema.openapi()
    except httpx.HTTPStatusError as e:
        _error(f"Failed to fetch schema: {e.response.text}")
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    paths = spec.get("paths", {})

    if command is None:
        # List all endpoints
        endpoints = []
        for path, methods in sorted(paths.items()):
            for method, details in methods.items():
                if method in ("get", "post", "put", "delete", "patch"):
                    endpoints.append(
                        {
                            "method": method.upper(),
                            "path": path,
                            "summary": details.get("summary", ""),
                        }
                    )
        _output({"endpoints": endpoints, "total": len(endpoints)})
        return

    # Map CLI commands to API paths
    command_map = {
        "auth.register": ("post", "/v1/agents/register"),
        "auth.status": ("get", "/v1/agents/me"),
        "submission.create": ("post", "/next/submit"),
        "bench.list": ("get", "/alive-tokens"),
        "bench.view": ("get", "/alive-tokens/{token_address}"),
    }

    if command in command_map:
        method, path = command_map[command]
        path_data = paths.get(path, {})
        method_data = path_data.get(method, {})
        if not method_data:
            _error(f"Endpoint {method.upper()} {path} not found in schema.")
        _output(_extract_endpoint_schema(method, path, method_data, spec))
        return

    # Try fuzzy match: search paths for the command string
    matches = []
    for path, methods in paths.items():
        for method, details in methods.items():
            if command.lower() in path.lower() or command.lower() in (details.get("summary", "")).lower():
                matches.append(_extract_endpoint_schema(method, path, details, spec))

    if matches:
        _output({"matches": matches, "total": len(matches)})
    else:
        _error(f"No endpoints matching '{command}'. Run 'alphakek schema' to see all.")


def _extract_endpoint_schema(method: str, path: str, details: dict, spec: dict) -> dict:
    """Extract a clean schema for one endpoint."""
    result: dict = {
        "method": method.upper(),
        "path": path,
        "summary": details.get("summary", ""),
        "description": details.get("description", ""),
    }

    # Parameters
    params = details.get("parameters", [])
    if params:
        result["parameters"] = [
            {
                "name": p.get("name"),
                "in": p.get("in"),
                "required": p.get("required", False),
                "description": p.get("description", ""),
                "schema": p.get("schema", {}),
            }
            for p in params
        ]

    # Request body — resolve $ref
    req_body = details.get("requestBody", {})
    if req_body:
        content = req_body.get("content", {})
        json_content = content.get("application/json", {})
        schema = json_content.get("schema", {})
        schema = _resolve_ref(schema, spec)
        result["request_body"] = schema

    # Responses
    responses = details.get("responses", {})
    if responses:
        result["responses"] = {}
        for status_code, resp_data in responses.items():
            resp_content = resp_data.get("content", {})
            resp_json = resp_content.get("application/json", {})
            resp_schema = resp_json.get("schema", {})
            resp_schema = _resolve_ref(resp_schema, spec)
            result["responses"][status_code] = {
                "description": resp_data.get("description", ""),
                "schema": resp_schema,
            }

    return result


def _resolve_ref(schema: dict, spec: dict) -> dict:
    """Resolve a single level of $ref in a JSON schema."""
    ref = schema.get("$ref")
    if not ref:
        return schema

    # Parse "#/components/schemas/ModelName"
    parts = ref.lstrip("#/").split("/")
    resolved = spec
    for part in parts:
        resolved = resolved.get(part, {})

    if isinstance(resolved, dict):
        return resolved
    return schema
