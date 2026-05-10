from __future__ import annotations

import json
import logging
from pathlib import Path

from .config import Settings
from .http import post_json

LOGGER = logging.getLogger(__name__)

UPLOAD_URL = "https://content.dropboxapi.com/2/files/upload"
SHARE_URL = "https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings"


def _dropbox_headers(token: str, remote_path: str) -> dict[str, str]:
    api_arg = json.dumps({
        "path": remote_path,
        "mode": "overwrite",
        "autorename": False,
        "mute": True,
    })
    return {
        "Authorization": f"Bearer {token}",
        "Dropbox-API-Arg": api_arg,
        "Content-Type": "application/octet-stream",
    }


def upload_to_dropbox(settings: Settings, local_path: Path, remote_folder: str = "/career-os") -> str | None:
    """Upload a file to Dropbox and return a public share link.

    Returns None if Dropbox is not configured or if the upload fails.
    """
    if not settings.dropbox_token or settings.dry_run:
        LOGGER.info("DRY RUN / no Dropbox token: would upload %s to %s", local_path.name, remote_folder)
        return None

    remote_path = f"{remote_folder}/{local_path.name}"

    # Upload the file using the content upload endpoint
    try:
        from urllib.request import Request, urlopen

        api_arg = json.dumps({
            "path": remote_path,
            "mode": "overwrite",
            "autorename": False,
            "mute": True,
        })
        headers = {
            "Authorization": f"Bearer {settings.dropbox_token}",
            "Dropbox-API-Arg": api_arg,
            "Content-Type": "application/octet-stream",
        }
        data = local_path.read_bytes()
        request = Request(UPLOAD_URL, data=data, headers=headers, method="POST")
        with urlopen(request, timeout=60) as response:
            response.read()
    except Exception as exc:
        LOGGER.error("Dropbox upload failed for %s: %s", local_path.name, exc)
        return None

    # Create a shared link
    try:
        result = post_json(
            SHARE_URL,
            {"path": remote_path, "settings": {"requested_visibility": "public"}},
            headers={
                "Authorization": f"Bearer {settings.dropbox_token}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        link = result.get("url", "")
        if link:
            LOGGER.info("Dropbox share link for %s: %s", local_path.name, link)
            return link
    except RuntimeError as exc:
        # If link already exists, Dropbox returns a conflict error with the existing link
        error_str = str(exc)
        if "shared_link_already_exists" in error_str:
            # Try to get the existing link
            try:
                existing = post_json(
                    "https://api.dropboxapi.com/2/sharing/list_shared_links",
                    {"path": remote_path, "direct_only": True},
                    headers={
                        "Authorization": f"Bearer {settings.dropbox_token}",
                        "Content-Type": "application/json",
                    },
                    timeout=30,
                )
                links = existing.get("links", [])
                if links:
                    link = links[0].get("url", "")
                    LOGGER.info("Dropbox existing share link for %s: %s", local_path.name, link)
                    return link
            except RuntimeError:
                pass
        LOGGER.error("Dropbox share link creation failed for %s: %s", local_path.name, exc)

    return None
