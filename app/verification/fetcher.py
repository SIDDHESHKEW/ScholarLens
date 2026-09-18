import ipaddress
import socket
from dataclasses import dataclass
from hashlib import sha256
from urllib.parse import urlparse

import httpx


@dataclass(frozen=True)
class FetchResult:
    url: str
    success: bool
    status_code: int | None = None
    content: str = ""
    content_hash: str | None = None
    error: str | None = None


def validate_source_url(url: str) -> tuple[bool, str | None]:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False, "Only http and https URLs are allowed."
    hostname = parsed.hostname.casefold()
    if hostname in {"localhost", "metadata.google.internal"} or hostname.endswith(".local"):
        return False, "Local and metadata hosts are not allowed."
    try:
        addresses = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False, "Host could not be resolved."
    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return False, "Private or local network addresses are not allowed."
    return True, None


def fetch_source(url: str, *, timeout: float = 10.0, max_bytes: int = 2_000_000) -> FetchResult:
    valid, error = validate_source_url(url)
    if not valid:
        return FetchResult(url=url, success=False, error=error)
    try:
        with httpx.Client(follow_redirects=False, timeout=timeout, headers={"User-Agent": "ScholarMatch-Verification/1.0"}) as client:
            response = client.get(url)
        if response.status_code in {301, 302, 303, 307, 308}:
            location = response.headers.get("location")
            if not location:
                return FetchResult(url=url, success=False, status_code=response.status_code, error="Redirect without location.")
            redirect_valid, redirect_error = validate_source_url(str(httpx.URL(url).join(location)))
            if not redirect_valid:
                return FetchResult(url=url, success=False, status_code=response.status_code, error=redirect_error)
            return fetch_source(str(httpx.URL(url).join(location)), timeout=timeout, max_bytes=max_bytes)
        if response.status_code >= 400:
            return FetchResult(url=url, success=False, status_code=response.status_code, error=f"HTTP {response.status_code}")
        content = response.content[: max_bytes + 1]
        if len(content) > max_bytes:
            return FetchResult(url=url, success=False, status_code=response.status_code, error="Response exceeds size limit.")
        text = content.decode(response.encoding or "utf-8", errors="replace")
        return FetchResult(url=url, success=True, status_code=response.status_code, content=text, content_hash=sha256(content).hexdigest())
    except (httpx.HTTPError, UnicodeError, TimeoutError) as error:
        return FetchResult(url=url, success=False, error=str(error))