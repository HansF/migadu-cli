"""Synchronous HTTP client for the Migadu API — the single source of truth.

This mirrors the Migadu API surface 1:1. Every method returns raw JSON
or raises MigaduAPIError with status_code and message.
"""

from __future__ import annotations

import base64
import json
import sys
from dataclasses import dataclass
from typing import Any

import requests


BASE_URL = "https://api.migadu.com/v1"


class MigaduAPIError(Exception):
    """Raised for non-success responses from the Migadu API."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(message)


@dataclass(frozen=True)
class Auth:
    """Migadu HTTP Basic auth credentials."""
    email: str
    api_key: str

    def header(self) -> dict[str, str]:
        credentials = base64.b64encode(f"{self.email}:{self.api_key}".encode()).decode()
        return {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }


class MigaduClient:
    """Synchronous HTTP client for Migadu API.

    Usage:
        client = MigaduClient(auth)
        domains = client.list_domains()
        client.create_domain("example.com", hosted_dns=False)
    """

    def __init__(self, auth: Auth, timeout: float = 30.0) -> None:
        self.auth = auth
        self.timeout = timeout
        self._session: requests.Session | None = None

    def _session_get(self) -> requests.Session:
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update(self.auth.header())
        return self._session

    def close(self) -> None:
        if self._session:
            self._session.close()
            self._session = None

    def __enter__(self) -> "MigaduClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # ──────────────────────────────────────────────────
    # Internal request helper
    # ──────────────────────────────────────────────────
    def _request(
        self,
        method: str,
        path: str,
        *,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{BASE_URL}{path}"
        try:
            resp = self._session_get().request(
                method,
                url,
                json=json_data,
                params=params,
                timeout=self.timeout,
            )
        except requests.RequestException as e:
            raise MigaduAPIError(0, f"Network error: {e}") from e

        if resp.status_code >= 400:
            # Migadu returns JSON error bodies; fall back to text
            try:
                err = resp.json()
                msg = json.dumps(err)
            except json.JSONDecodeError:
                msg = resp.text
            raise MigaduAPIError(resp.status_code, msg)

        if not resp.content:
            return {}
        return resp.json()  # type: ignore[no-any-return]

    def _get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return self._request("GET", path, **kwargs)

    def _post(self, path: str, json_data: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        return self._request("POST", path, json_data=json_data, **kwargs)

    def _patch(self, path: str, json_data: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        return self._request("PATCH", path, json_data=json_data, **kwargs)

    def _put(self, path: str, json_data: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        return self._request("PUT", path, json_data=json_data, **kwargs)

    def _delete(self, path: str) -> None:
        """DELETE returns None on success.

        Migadu quirk: successful DELETE may return HTTP 500.
        This treats 200, 204, 404, 500 as success (idempotent).
        """
        url = f"{BASE_URL}{path}"
        resp = self._session_get().request("DELETE", url, timeout=self.timeout)
        if resp.status_code not in (200, 204, 404, 500):
            try:
                err = resp.json()
                msg = json.dumps(err)
            except json.JSONDecodeError:
                msg = resp.text
            raise MigaduAPIError(resp.status_code, msg)
        return None

    # ──────────────────────────────────────────────────
    # Domain endpoints
    # ──────────────────────────────────────────────────
    def list_domains(self) -> dict[str, Any]:
        return self._get("/domains")

    def get_domain(self, name: str) -> dict[str, Any]:
        return self._get(f"/domains/{name}")

    def create_domain(
        self,
        name: str,
        hosted_dns: bool = False,
        create_default_addresses: bool = True,
    ) -> dict[str, Any]:
        return self._post(
            "/domains",
            json_data={
                "name": name,
                "hosted_dns": hosted_dns,
                "create_default_addresses": create_default_addresses,
            },
        )

    def update_domain(
        self,
        name: str,
        description: str | None = None,
        tags: str | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if description is not None:
            data["description"] = description
        if tags is not None:
            data["tags"] = tags
        return self._patch(f"/domains/{name}", json_data=data)

    def get_domain_records(self, name: str) -> dict[str, Any]:
        return self._get(f"/domains/{name}/records")

    def get_domain_diagnostics(self, name: str) -> dict[str, Any]:
        return self._get(f"/domains/{name}/diagnostics")

    def activate_domain(self, name: str) -> dict[str, Any]:
        return self._get(f"/domains/{name}/activate")

    def get_domain_usage(self, name: str) -> dict[str, Any]:
        return self._get(f"/domains/{name}/usage")

    # ──────────────────────────────────────────────────
    # Mailbox endpoints
    # ──────────────────────────────────────────────────
    def list_mailboxes(self, domain: str) -> dict[str, Any]:
        return self._get(f"/domains/{domain}/mailboxes")

    def get_mailbox(self, domain: str, local_part: str) -> dict[str, Any]:
        return self._get(f"/domains/{domain}/mailboxes/{local_part}")

    def create_mailbox(
        self,
        domain: str,
        local_part: str,
        *,
        name: str | None = None,
        password: str | None = None,
        password_method: str = "password",
        password_recovery_email: str | None = None,
        forwarding_to: str | None = None,
        is_internal: bool = False,
        wildcard_sender: bool = False,
        may_send: bool = True,
        may_receive: bool = True,
        may_access_imap: bool = True,
        may_access_pop3: bool = True,
        may_access_managesieve: bool = False,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {"local_part": local_part}
        if name is not None:
            data["name"] = name
        if password is not None:
            data["password"] = password
        if password_method:
            data["password_method"] = password_method
        if password_recovery_email is not None:
            data["password_recovery_email"] = password_recovery_email
        if forwarding_to is not None:
            data["forwarding_to"] = forwarding_to
        if is_internal:
            data["is_internal"] = is_internal
        if wildcard_sender:
            data["wildcard_sender"] = wildcard_sender
        if not may_send:
            data["may_send"] = may_send
        if not may_receive:
            data["may_receive"] = may_receive
        if not may_access_imap:
            data["may_access_imap"] = may_access_imap
        if not may_access_pop3:
            data["may_access_pop3"] = may_access_pop3
        if may_access_managesieve:
            data["may_access_managesieve"] = may_access_managesieve
        return self._post(f"/domains/{domain}/mailboxes", json_data=data)

    def update_mailbox(
        self,
        domain: str,
        local_part: str,
        *,
        name: str | None = None,
        password: str | None = None,
        password_method: str | None = None,
        password_recovery_email: str | None = None,
        forwarding_to: str | None = None,
        is_internal: bool | None = None,
        wildcard_sender: bool | None = None,
        may_send: bool | None = None,
        may_receive: bool | None = None,
        may_access_imap: bool | None = None,
        may_access_pop3: bool | None = None,
        may_access_managesieve: bool | None = None,
        spam_action: str | None = None,
        spam_aggressiveness: str | None = None,
        sender_denylist: str | None = None,
        sender_allowlist: str | None = None,
        recipient_denylist: str | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if password is not None:
            data["password"] = password
        if password_method is not None:
            data["password_method"] = password_method
        if password_recovery_email is not None:
            data["password_recovery_email"] = password_recovery_email
        if forwarding_to is not None:
            data["forwarding_to"] = forwarding_to
        if is_internal is not None:
            data["is_internal"] = is_internal
        if wildcard_sender is not None:
            data["wildcard_sender"] = wildcard_sender
        if may_send is not None:
            data["may_send"] = may_send
        if may_receive is not None:
            data["may_receive"] = may_receive
        if may_access_imap is not None:
            data["may_access_imap"] = may_access_imap
        if may_access_pop3 is not None:
            data["may_access_pop3"] = may_access_pop3
        if may_access_managesieve is not None:
            data["may_access_managesieve"] = may_access_managesieve
        if spam_action is not None:
            data["spam_action"] = spam_action
        if spam_aggressiveness is not None:
            data["spam_aggressiveness"] = spam_aggressiveness
        if sender_denylist is not None:
            data["sender_denylist"] = sender_denylist
        if sender_allowlist is not None:
            data["sender_allowlist"] = sender_allowlist
        if recipient_denylist is not None:
            data["recipient_denylist"] = recipient_denylist
        return self._put(f"/domains/{domain}/mailboxes/{local_part}", json_data=data)

    def delete_mailbox(self, domain: str, local_part: str) -> None:
        self._delete(f"/domains/{domain}/mailboxes/{local_part}")

    def reset_mailbox_password(self, domain: str, local_part: str, password: str) -> dict[str, Any]:
        return self._post(f"/domains/{domain}/mailboxes/{local_part}/password", json_data={"password": password})

    def set_autoresponder(
        self,
        domain: str,
        local_part: str,
        *,
        enabled: bool = True,
        subject: str | None = None,
        message: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {"enabled": enabled}
        if subject is not None:
            data["subject"] = subject
        if message is not None:
            data["message"] = message
        if start_date is not None:
            data["start_date"] = start_date
        if end_date is not None:
            data["end_date"] = end_date
        return self._post(f"/domains/{domain}/mailboxes/{local_part}/autoresponder", json_data=data)

    # ──────────────────────────────────────────────────
    # Alias endpoints
    # ──────────────────────────────────────────────────
    def list_aliases(self, domain: str) -> dict[str, Any]:
        return self._get(f"/domains/{domain}/aliases")

    def get_alias(self, domain: str, local_part: str) -> dict[str, Any]:
        return self._get(f"/domains/{domain}/aliases/{local_part}")

    def create_alias(
        self,
        domain: str,
        local_part: str,
        destinations: list[str] | str,
        is_internal: bool = False,
    ) -> dict[str, Any]:
        if isinstance(destinations, str):
            destinations = [d.strip() for d in destinations.split(",")]
        return self._post(
            f"/domains/{domain}/aliases",
            json_data={
                "local_part": local_part,
                "destinations": destinations,
                "is_internal": is_internal,
            },
        )

    def update_alias(
        self,
        domain: str,
        local_part: str,
        destinations: list[str] | str | None = None,
        is_internal: bool | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if destinations is not None:
            if isinstance(destinations, str):
                destinations = [d.strip() for d in destinations.split(",")]
            data["destinations"] = destinations
        if is_internal is not None:
            data["is_internal"] = is_internal
        return self._put(f"/domains/{domain}/aliases/{local_part}", json_data=data)

    def delete_alias(self, domain: str, local_part: str) -> None:
        self._delete(f"/domains/{domain}/aliases/{local_part}")

    # ──────────────────────────────────────────────────
    # Identity endpoints
    # ──────────────────────────────────────────────────
    def list_identities(self, domain: str, mailbox: str) -> dict[str, Any]:
        return self._get(f"/domains/{domain}/mailboxes/{mailbox}/identities")

    def get_identity(self, domain: str, mailbox: str, local_part: str) -> dict[str, Any]:
        return self._get(f"/domains/{domain}/mailboxes/{mailbox}/identities/{local_part}")

    def create_identity(
        self,
        domain: str,
        mailbox: str,
        local_part: str,
        *,
        name: str | None = None,
        password_use: str = "none",
        password: str | None = None,
        may_send: bool = True,
        may_receive: bool = True,
        may_access_imap: bool = True,
        may_access_pop3: bool = True,
        may_access_managesieve: bool = False,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {"local_part": local_part, "password_use": password_use}
        if name is not None:
            data["name"] = name
        if password is not None:
            data["password"] = password
        if not may_send:
            data["may_send"] = may_send
        if not may_receive:
            data["may_receive"] = may_receive
        if not may_access_imap:
            data["may_access_imap"] = may_access_imap
        if not may_access_pop3:
            data["may_access_pop3"] = may_access_pop3
        if may_access_managesieve:
            data["may_access_managesieve"] = may_access_managesieve
        return self._post(f"/domains/{domain}/mailboxes/{mailbox}/identities", json_data=data)

    def update_identity(
        self,
        domain: str,
        mailbox: str,
        local_part: str,
        *,
        name: str | None = None,
        password: str | None = None,
        password_use: str | None = None,
        may_send: bool | None = None,
        may_receive: bool | None = None,
        may_access_imap: bool | None = None,
        may_access_pop3: bool | None = None,
        may_access_managesieve: bool | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if password is not None:
            data["password"] = password
        if password_use is not None:
            data["password_use"] = password_use
        if may_send is not None:
            data["may_send"] = may_send
        if may_receive is not None:
            data["may_receive"] = may_receive
        if may_access_imap is not None:
            data["may_access_imap"] = may_access_imap
        if may_access_pop3 is not None:
            data["may_access_pop3"] = may_access_pop3
        if may_access_managesieve is not None:
            data["may_access_managesieve"] = may_access_managesieve
        return self._put(f"/domains/{domain}/mailboxes/{mailbox}/identities/{local_part}", json_data=data)

    def delete_identity(self, domain: str, mailbox: str, local_part: str) -> None:
        self._delete(f"/domains/{domain}/mailboxes/{mailbox}/identities/{local_part}")

    # ──────────────────────────────────────────────────
    # Forwarding endpoints
    # ──────────────────────────────────────────────────
    def list_forwardings(self, domain: str, mailbox: str) -> dict[str, Any]:
        return self._get(f"/domains/{domain}/mailboxes/{mailbox}/forwardings")

    def get_forwarding(self, domain: str, mailbox: str, address: str) -> dict[str, Any]:
        return self._get(f"/domains/{domain}/mailboxes/{mailbox}/forwardings/{address}")

    def create_forwarding(
        self,
        domain: str,
        mailbox: str,
        address: str,
        *,
        expires_on: str | None = None,
        remove_upon_expiry: bool | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {"address": address}
        if expires_on is not None:
            data["expires_on"] = expires_on
        if remove_upon_expiry is not None:
            data["remove_upon_expiry"] = remove_upon_expiry
        return self._post(f"/domains/{domain}/mailboxes/{mailbox}/forwardings", json_data=data)

    def update_forwarding(
        self,
        domain: str,
        mailbox: str,
        address: str,
        *,
        is_active: bool | None = None,
        expires_on: str | None = None,
        remove_upon_expiry: bool | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if is_active is not None:
            data["is_active"] = is_active
        if expires_on is not None:
            data["expires_on"] = expires_on
        if remove_upon_expiry is not None:
            data["remove_upon_expiry"] = remove_upon_expiry
        return self._put(f"/domains/{domain}/mailboxes/{mailbox}/forwardings/{address}", json_data=data)

    def delete_forwarding(self, domain: str, mailbox: str, address: str) -> None:
        self._delete(f"/domains/{domain}/mailboxes/{mailbox}/forwardings/{address}")

    # ──────────────────────────────────────────────────
    # Rewrite endpoints
    # ──────────────────────────────────────────────────
    def list_rewrites(self, domain: str) -> dict[str, Any]:
        return self._get(f"/domains/{domain}/rewrites")

    def get_rewrite(self, domain: str, name: str) -> dict[str, Any]:
        return self._get(f"/domains/{domain}/rewrites/{name}")

    def create_rewrite(
        self,
        domain: str,
        name: str,
        local_part_rule: str,
        destinations: list[str] | str,
    ) -> dict[str, Any]:
        if isinstance(destinations, str):
            destinations = [d.strip() for d in destinations.split(",")]
        return self._post(
            f"/domains/{domain}/rewrites",
            json_data={
                "name": name,
                "local_part_rule": local_part_rule,
                "destinations": destinations,
            },
        )

    def update_rewrite(
        self,
        domain: str,
        name: str,
        *,
        new_name: str | None = None,
        local_part_rule: str | None = None,
        destinations: list[str] | str | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if new_name is not None:
            data["name"] = new_name
        if local_part_rule is not None:
            data["local_part_rule"] = local_part_rule
        if destinations is not None:
            if isinstance(destinations, str):
                destinations = [d.strip() for d in destinations.split(",")]
            data["destinations"] = destinations
        return self._put(f"/domains/{domain}/rewrites/{name}", json_data=data)

    def delete_rewrite(self, domain: str, name: str) -> None:
        self._delete(f"/domains/{domain}/rewrites/{name}")