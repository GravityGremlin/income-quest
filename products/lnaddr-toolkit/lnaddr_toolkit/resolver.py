"""Lightning Address resolution via LNURL-pay protocol.

Resolves a Lightning Address (user@domain) to its LNURL-pay endpoint
and fetches pay metadata (min/max sendable, comment allowance, etc.).
"""

import json
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin

import requests

from .exceptions import ResolutionError
from .validator import parse_lightning_address, validate_lightning_address


@dataclass
class LNURLPayMetadata:
    """Metadata returned by LNURL-pay endpoint."""
    callback: str
    min_sendable: int  # millisatoshis
    max_sendable: int  # millisatoshis
    metadata: str  # JSON string with description, etc.
    comment_allowed: int  # max comment length in chars
    tag: str = "payRequest"
    allows_nostr: Optional[bool] = None
    nostr_pubkey: Optional[str] = None

    @property
    def min_sats(self) -> int:
        """Minimum sendable in satoshis."""
        return self.min_sendable // 1000

    @property
    def max_sats(self) -> int:
        """Maximum sendable in satoshis."""
        return self.max_sendable // 1000

    def parse_metadata(self) -> list:
        """Parse the metadata JSON string into a list of [type, value] pairs."""
        try:
            return json.loads(self.metadata)
        except json.JSONDecodeError:
            return []

    def get_text_description(self) -> str:
        """Extract text/plain description from metadata."""
        for item in self.parse_metadata():
            if isinstance(item, list) and len(item) == 2 and item[0] == "text/plain":
                return item[1]
        return ""

    def get_image_url(self) -> Optional[str]:
        """Extract image/png or image/jpeg URL from metadata."""
        for item in self.parse_metadata():
            if isinstance(item, list) and len(item) == 2 and item[0] in ("image/png", "image/jpeg"):
                return item[1]
        return None


def _build_lnurl_pay_url(local_part: str, domain: str) -> str:
    """Construct the LNURL-pay well-known URL for a Lightning Address."""
    # Per LNURL spec: https://domain/.well-known/lnurlp/user
    return f"https://{domain}/.well-known/lnurlp/{local_part}"


def resolve_lightning_address(
    address: str,
    timeout: int = 10,
    session: Optional[requests.Session] = None
) -> LNURLPayMetadata:
    """
    Resolve a Lightning Address to its LNURL-pay metadata.

    Args:
        address: Lightning Address (e.g., "user@domain.com")
        timeout: Request timeout in seconds
        session: Optional requests.Session for connection pooling

    Returns:
        LNURLPayMetadata with callback URL, min/max sendable, etc.

    Raises:
        ValidationError: If address format is invalid
        ResolutionError: If resolution fails (network, HTTP error, invalid response)
    """
    validate_lightning_address(address)
    local_part, domain = parse_lightning_address(address)

    url = _build_lnurl_pay_url(local_part, domain)

    try:
        if session:
            response = session.get(url, timeout=timeout, headers={"Accept": "application/json"})
        else:
            response = requests.get(url, timeout=timeout, headers={"Accept": "application/json"})

        response.raise_for_status()
        data = response.json()

        # Validate required fields per LNURL-pay spec
        required_fields = ["callback", "minSendable", "maxSendable", "metadata", "tag"]
        for field in required_fields:
            if field not in data:
                raise ResolutionError(f"Missing required field '{field}' in LNURL-pay response")

        if data.get("tag") != "payRequest":
            raise ResolutionError(f"Unexpected tag: {data.get('tag')}, expected 'payRequest'")

        return LNURLPayMetadata(
            callback=data["callback"],
            min_sendable=int(data["minSendable"]),
            max_sendable=int(data["maxSendable"]),
            metadata=data["metadata"],
            comment_allowed=int(data.get("commentAllowed", 0)),
            tag=data["tag"],
            allows_nostr=data.get("allowsNostr"),
            nostr_pubkey=data.get("nostrPubkey"),
        )

    except requests.exceptions.Timeout:
        raise ResolutionError(f"Request timeout resolving {address} at {url}")
    except requests.exceptions.ConnectionError as e:
        raise ResolutionError(f"Connection error resolving {address}: {e}")
    except requests.exceptions.HTTPError as e:
        raise ResolutionError(f"HTTP error resolving {address}: {e.response.status_code} {e.response.reason}")
    except json.JSONDecodeError as e:
        raise ResolutionError(f"Invalid JSON response from {url}: {e}")
    except (KeyError, ValueError, TypeError) as e:
        raise ResolutionError(f"Malformed LNURL-pay response: {e}")


def fetch_lnurl_pay_metadata(
    address: str,
    timeout: int = 10,
    session: Optional[requests.Session] = None
) -> LNURLPayMetadata:
    """
    Alias for resolve_lightning_address for semantic clarity.

    Args:
        address: Lightning Address (e.g., "user@domain.com")
        timeout: Request timeout in seconds
        session: Optional requests.Session for connection pooling

    Returns:
        LNURLPayMetadata
    """
    return resolve_lightning_address(address, timeout, session)