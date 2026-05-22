"""Remote HTTP transport for the Linta MCP server."""

from __future__ import annotations

import json
import os
import time
from base64 import b64decode, urlsafe_b64encode
from dataclasses import dataclass
from hashlib import sha256
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from secrets import token_urlsafe
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

from linta import __version__
from linta.mcp_server import ReadOnlyMcpServer

DEFAULT_REMOTE_TOKEN_ENV = "LINTA_REMOTE_MCP_TOKEN"
DEFAULT_OAUTH_CLIENT_ID_ENV = "LINTA_OAUTH_CLIENT_ID"
DEFAULT_OAUTH_CLIENT_SECRET_ENV = "LINTA_OAUTH_CLIENT_SECRET"
DEFAULT_OAUTH_APPROVAL_TOKEN_ENV = "LINTA_OAUTH_APPROVAL_TOKEN"
DEFAULT_OAUTH_PUBLIC_BASE_URL_ENV = "LINTA_REMOTE_MCP_PUBLIC_BASE_URL"
DEFAULT_OAUTH_TOKEN_STORE_ENV = "LINTA_OAUTH_TOKEN_STORE"
OAUTH_ACCESS_TOKEN_TTL_SECONDS = 60 * 60 * 24 * 30
OAUTH_AUTHORIZATION_CODE_TTL_SECONDS = 60 * 10


@dataclass(frozen=True)
class RemoteMcpConfig:
    kb_root: Path
    agent: str
    host: str
    port: int
    token: str | None
    path: str = "/mcp"
    public_base_url: str | None = None
    oauth_client_id: str | None = None
    oauth_client_secret: str | None = None
    oauth_approval_token: str | None = None
    oauth_token_store: Path | None = None

    @property
    def oauth_enabled(self) -> bool:
        return all(
            (
                self.public_base_url,
                self.oauth_client_id,
                self.oauth_client_secret,
                self.oauth_approval_token,
            )
        )


class RemoteMcpError(Exception):
    """Remote MCP configuration error."""


def token_from_env(env_name: str = DEFAULT_REMOTE_TOKEN_ENV) -> str:
    token = os.environ.get(env_name, "").strip()
    if not token:
        raise RemoteMcpError(f"Missing bearer token. Set {env_name}.")
    return token


@dataclass(frozen=True)
class RemoteMcpAuthEnv:
    token: str | None
    public_base_url: str | None
    oauth_client_id: str | None
    oauth_client_secret: str | None
    oauth_approval_token: str | None


@dataclass(frozen=True)
class OAuthAuthorizationCode:
    client_id: str
    redirect_uri: str
    code_challenge: str | None
    code_challenge_method: str | None
    scope: str
    expires_at: float


class OAuthMemoryStore:
    """In-memory OAuth state for a single-user connector process."""

    def __init__(self, *, token_store_path: Path | None = None) -> None:
        self.token_store_path = token_store_path
        self._codes: dict[str, OAuthAuthorizationCode] = {}
        self._tokens: dict[str, float] = self._load_tokens()

    def create_code(
        self,
        *,
        client_id: str,
        redirect_uri: str,
        code_challenge: str | None,
        code_challenge_method: str | None,
        scope: str,
    ) -> str:
        code = token_urlsafe(32)
        self._codes[code] = OAuthAuthorizationCode(
            client_id=client_id,
            redirect_uri=redirect_uri,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            scope=scope,
            expires_at=time.time() + OAUTH_AUTHORIZATION_CODE_TTL_SECONDS,
        )
        return code

    def exchange_code(
        self,
        *,
        code: str,
        client_id: str,
        redirect_uri: str,
        code_verifier: str | None,
    ) -> str:
        record = self._codes.pop(code, None)
        if record is None:
            raise RemoteMcpError("Invalid authorization code.")
        if record.expires_at < time.time():
            raise RemoteMcpError("Authorization code expired.")
        if record.client_id != client_id or record.redirect_uri != redirect_uri:
            raise RemoteMcpError("Authorization code metadata mismatch.")
        _verify_pkce(record, code_verifier)
        access_token = token_urlsafe(32)
        self._tokens[_hash_token(access_token)] = time.time() + OAUTH_ACCESS_TOKEN_TTL_SECONDS
        self._save_tokens()
        return access_token

    def validate_access_token(self, access_token: str) -> bool:
        token_hash = _hash_token(access_token)
        expires_at = self._tokens.get(token_hash)
        if expires_at is None:
            return False
        if expires_at < time.time():
            self._tokens.pop(token_hash, None)
            self._save_tokens()
            return False
        return True

    def _load_tokens(self) -> dict[str, float]:
        if self.token_store_path is None or not self.token_store_path.exists():
            return {}
        try:
            raw = json.loads(self.token_store_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        now = time.time()
        tokens = raw.get("tokens") if isinstance(raw, dict) else {}
        if not isinstance(tokens, dict):
            return {}
        return {
            str(token_hash): float(expires_at)
            for token_hash, expires_at in tokens.items()
            if float(expires_at) > now
        }

    def _save_tokens(self) -> None:
        if self.token_store_path is None:
            return
        now = time.time()
        self._tokens = {
            token_hash: expires_at
            for token_hash, expires_at in self._tokens.items()
            if expires_at > now
        }
        self.token_store_path.parent.mkdir(parents=True, exist_ok=True)
        self.token_store_path.write_text(
            json.dumps({"tokens": self._tokens}, indent=2) + "\n",
            encoding="utf-8",
        )
        self.token_store_path.chmod(0o600)


def remote_auth_from_env(
    *,
    token_env: str = DEFAULT_REMOTE_TOKEN_ENV,
    public_base_url: str | None = None,
    public_base_url_env: str = DEFAULT_OAUTH_PUBLIC_BASE_URL_ENV,
    oauth_client_id_env: str = DEFAULT_OAUTH_CLIENT_ID_ENV,
    oauth_client_secret_env: str = DEFAULT_OAUTH_CLIENT_SECRET_ENV,
    oauth_approval_token_env: str = DEFAULT_OAUTH_APPROVAL_TOKEN_ENV,
) -> RemoteMcpAuthEnv:
    token = os.environ.get(token_env, "").strip() or None
    base_url = public_base_url or os.environ.get(public_base_url_env, "").strip() or None
    client_id = os.environ.get(oauth_client_id_env, "").strip() or None
    client_secret = os.environ.get(oauth_client_secret_env, "").strip() or None
    approval_token = os.environ.get(oauth_approval_token_env, "").strip() or None
    oauth_values = (base_url, client_id, client_secret, approval_token)
    if any(oauth_values) and not all(oauth_values):
        raise RemoteMcpError(
            "OAuth configuration is incomplete. Set public base URL, client ID, "
            "client secret, and approval token."
        )
    if not token and not all(oauth_values):
        raise RemoteMcpError(
            f"Missing auth configuration. Set {token_env} for bearer auth or configure OAuth."
        )
    return RemoteMcpAuthEnv(
        token=token,
        public_base_url=_normalize_public_base_url(base_url) if base_url else None,
        oauth_client_id=client_id,
        oauth_client_secret=client_secret,
        oauth_approval_token=approval_token,
    )


def serve_remote_mcp(config: RemoteMcpConfig) -> None:
    """Serve JSON-RPC MCP requests over HTTP."""

    httpd = make_remote_mcp_http_server(config)
    httpd.serve_forever()


def make_remote_mcp_http_server(config: RemoteMcpConfig) -> ThreadingHTTPServer:
    """Build a remote MCP HTTP server without starting it."""

    mcp_server = ReadOnlyMcpServer(kb_root=config.kb_root, agent=config.agent)
    handler = _build_handler(
        mcp_server=mcp_server,
        config=config,
        oauth_store=OAuthMemoryStore(token_store_path=_oauth_token_store_path(config)),
    )
    return ThreadingHTTPServer((config.host, config.port), handler)


def handle_remote_jsonrpc(
    *,
    kb_root: Path,
    agent: str,
    payload: dict[str, Any],
) -> dict[str, Any] | None:
    """Handle one JSON-RPC payload without HTTP; used by tests."""

    return ReadOnlyMcpServer(kb_root=kb_root, agent=agent).handle_request(payload)


def _build_handler(
    *,
    mcp_server: ReadOnlyMcpServer,
    config: RemoteMcpConfig,
    oauth_store: OAuthMemoryStore,
) -> type[BaseHTTPRequestHandler]:
    class LintaRemoteMcpHandler(BaseHTTPRequestHandler):
        server_version = f"LintaRemoteMCP/{__version__}"

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/health":
                self._write_json(
                    200,
                    {
                        "ok": True,
                        "name": "linta",
                        "version": __version__,
                        "agent": config.agent,
                        "oauth_enabled": config.oauth_enabled,
                    },
                )
                return
            if parsed.path in _protected_resource_metadata_paths(config):
                self._write_json(200, _protected_resource_metadata(config))
                return
            if parsed.path == "/.well-known/oauth-authorization-server":
                self._write_json(200, _authorization_server_metadata(config))
                return
            if parsed.path == "/oauth/authorize":
                self._write_html(200, _authorization_form(parsed.query))
                return
            self._write_json(404, {"error": "not_found"})

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/oauth/authorize":
                self._handle_authorize_post()
                return
            if parsed.path == "/oauth/token":
                self._handle_token_post()
                return
            if parsed.path != config.path:
                self._write_json(404, {"error": "not_found"})
                return
            if not _is_authorized(
                self.headers.get("Authorization"),
                config.token,
                oauth_store=oauth_store,
            ):
                self._write_json(
                    401,
                    {"error": "unauthorized"},
                    headers={"WWW-Authenticate": _www_authenticate(config)},
                )
                return
            length = int(self.headers.get("Content-Length") or "0")
            if length <= 0:
                self._write_json(400, {"error": "empty_request"})
                return
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except json.JSONDecodeError as error:
                self._write_json(400, {"error": "invalid_json", "message": str(error)})
                return
            response = mcp_server.handle_request(payload)
            if response is None:
                self._write_json(202, {"ok": True})
                return
            self._write_json(200, response)

        def _handle_authorize_post(self) -> None:
            if not config.oauth_enabled:
                self._write_json(404, {"error": "oauth_not_configured"})
                return
            form = self._read_form()
            try:
                _validate_authorization_request(form, config)
                if _first(form, "approval_token") != config.oauth_approval_token:
                    raise RemoteMcpError("Invalid approval token.")
                code = oauth_store.create_code(
                    client_id=_first(form, "client_id"),
                    redirect_uri=_first(form, "redirect_uri"),
                    code_challenge=_optional_first(form, "code_challenge"),
                    code_challenge_method=_optional_first(form, "code_challenge_method"),
                    scope=_optional_first(form, "scope") or "linta:read",
                )
                redirect = _append_query(
                    _first(form, "redirect_uri"),
                    {
                        "code": code,
                        "state": _optional_first(form, "state"),
                    },
                )
            except RemoteMcpError as error:
                self._write_html(400, f"<h1>Authorization failed</h1><p>{escape(str(error))}</p>")
                return
            self.send_response(302)
            self.send_header("Location", redirect)
            self.end_headers()

        def _handle_token_post(self) -> None:
            if not config.oauth_enabled:
                self._write_json(404, {"error": "oauth_not_configured"})
                return
            form = self._read_form()
            try:
                client_id, client_secret = _client_credentials(
                    self.headers.get("Authorization"), form
                )
                if (
                    client_id != config.oauth_client_id
                    or client_secret != config.oauth_client_secret
                ):
                    raise RemoteMcpError("Invalid OAuth client credentials.")
                if _first(form, "grant_type") != "authorization_code":
                    raise RemoteMcpError("Unsupported grant_type.")
                access_token = oauth_store.exchange_code(
                    code=_first(form, "code"),
                    client_id=client_id,
                    redirect_uri=_first(form, "redirect_uri"),
                    code_verifier=_optional_first(form, "code_verifier"),
                )
            except RemoteMcpError as error:
                self._write_json(
                    400,
                    {"error": "invalid_grant", "error_description": str(error)},
                )
                return
            self._write_json(
                200,
                {
                    "access_token": access_token,
                    "token_type": "Bearer",
                    "expires_in": OAUTH_ACCESS_TOKEN_TTL_SECONDS,
                    "scope": _optional_first(form, "scope") or "linta:read",
                },
            )

        def _read_form(self) -> dict[str, list[str]]:
            length = int(self.headers.get("Content-Length") or "0")
            if length <= 0:
                return {}
            return parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)

        def log_message(self, format: str, *args: object) -> None:
            return

        def _write_json(
            self,
            status: int,
            payload: dict[str, Any],
            *,
            headers: dict[str, str] | None = None,
        ) -> None:
            body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            for key, value in (headers or {}).items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body)

        def _write_html(self, status: int, html: str) -> None:
            body = html.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return LintaRemoteMcpHandler


def _is_authorized(
    header: str | None,
    token: str | None,
    *,
    oauth_store: OAuthMemoryStore | None = None,
) -> bool:
    if not header:
        return False
    scheme, _, value = header.partition(" ")
    if scheme.lower() != "bearer":
        return False
    bearer = value.strip()
    if token and bearer == token:
        return True
    return oauth_store.validate_access_token(bearer) if oauth_store else False


def _hash_token(access_token: str) -> str:
    return sha256(access_token.encode("utf-8")).hexdigest()


def _oauth_token_store_path(config: RemoteMcpConfig) -> Path | None:
    if not config.oauth_enabled:
        return None
    if config.oauth_token_store is not None:
        return config.oauth_token_store.expanduser().resolve()
    configured = os.environ.get(DEFAULT_OAUTH_TOKEN_STORE_ENV, "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return Path.home() / ".linta-connector/oauth_tokens.json"


def _protected_resource_metadata(config: RemoteMcpConfig) -> dict[str, Any]:
    base_url = _require_oauth_base_url(config)
    return {
        "resource": f"{base_url}{config.path}",
        "authorization_servers": [base_url],
        "bearer_methods_supported": ["header"],
        "scopes_supported": ["linta:read", "linta:write"],
    }


def _authorization_server_metadata(config: RemoteMcpConfig) -> dict[str, Any]:
    base_url = _require_oauth_base_url(config)
    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/oauth/authorize",
        "token_endpoint": f"{base_url}/oauth/token",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "code_challenge_methods_supported": ["S256", "plain"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post"],
        "scopes_supported": ["linta:read", "linta:write"],
    }


def _protected_resource_metadata_paths(config: RemoteMcpConfig) -> set[str]:
    return {
        "/.well-known/oauth-protected-resource",
        f"/.well-known/oauth-protected-resource{config.path}",
    }


def _www_authenticate(config: RemoteMcpConfig) -> str:
    if config.oauth_enabled:
        metadata_url = f"{_require_oauth_base_url(config)}/.well-known/oauth-protected-resource"
        return (
            'Bearer realm="linta-remote-mcp", '
            f'resource_metadata="{metadata_url}", scope="linta:read"'
        )
    return 'Bearer realm="linta-remote-mcp"'


def _authorization_form(query: str) -> str:
    params = parse_qs(query, keep_blank_values=True)
    hidden = "\n".join(
        f'<input type="hidden" name="{escape(key)}" value="{escape(values[0])}">'
        for key, values in sorted(params.items())
        if values
    )
    return f"""<!doctype html>
<html>
  <head><meta charset="utf-8"><title>Authorize Linta</title></head>
  <body>
    <h1>Authorize Linta Connector</h1>
    <p>Enter your private Linta approval token to connect Claude.</p>
    <form method="post" action="/oauth/authorize">
      {hidden}
      <label>Approval token <input name="approval_token" type="password" autofocus></label>
      <button type="submit">Authorize</button>
    </form>
  </body>
</html>
"""


def _validate_authorization_request(
    form: dict[str, list[str]],
    config: RemoteMcpConfig,
) -> None:
    if _first(form, "response_type") != "code":
        raise RemoteMcpError("Unsupported response_type.")
    if _first(form, "client_id") != config.oauth_client_id:
        raise RemoteMcpError("Invalid OAuth client ID.")
    redirect_uri = _first(form, "redirect_uri")
    if not redirect_uri.startswith("https://") and not redirect_uri.startswith("http://localhost"):
        raise RemoteMcpError("Redirect URI must use HTTPS or localhost.")


def _verify_pkce(record: OAuthAuthorizationCode, code_verifier: str | None) -> None:
    if not record.code_challenge:
        return
    if not code_verifier:
        raise RemoteMcpError("Missing PKCE code_verifier.")
    method = record.code_challenge_method or "plain"
    if method == "plain":
        actual = code_verifier
    elif method == "S256":
        actual = (
            urlsafe_b64encode(sha256(code_verifier.encode("utf-8")).digest())
            .decode("ascii")
            .rstrip("=")
        )
    else:
        raise RemoteMcpError("Unsupported PKCE code_challenge_method.")
    if actual != record.code_challenge:
        raise RemoteMcpError("PKCE verification failed.")


def _client_credentials(
    authorization_header: str | None,
    form: dict[str, list[str]],
) -> tuple[str, str]:
    if authorization_header:
        scheme, _, value = authorization_header.partition(" ")
        if scheme.lower() == "basic":
            decoded = b64decode(value).decode("utf-8")
            client_id, _, client_secret = decoded.partition(":")
            return client_id, client_secret
    return _first(form, "client_id"), _first(form, "client_secret")


def _first(form: dict[str, list[str]], key: str) -> str:
    value = _optional_first(form, key)
    if value is None:
        raise RemoteMcpError(f"Missing {key}.")
    return value


def _optional_first(form: dict[str, list[str]], key: str) -> str | None:
    values = form.get(key)
    if not values:
        return None
    return values[0]


def _append_query(url: str, params: dict[str, str | None]) -> str:
    clean = {key: value for key, value in params.items() if value}
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}{urlencode(clean)}" if clean else url


def _normalize_public_base_url(value: str) -> str:
    normalized = value.strip().rstrip("/")
    if not normalized.startswith("https://") and not normalized.startswith("http://localhost"):
        raise RemoteMcpError("OAuth public base URL must use HTTPS or localhost.")
    return normalized


def _require_oauth_base_url(config: RemoteMcpConfig) -> str:
    if not config.public_base_url:
        raise RemoteMcpError("OAuth public base URL is not configured.")
    return config.public_base_url
