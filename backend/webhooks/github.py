from flask import Request
import hashlib
import hmac
import json
import logging
from werkzeug.exceptions import BadRequest, InternalServerError

from backend.generics import config, get_repo_config_by_url

logger = logging.getLogger("k8s_autobuilder.backend.webhooks.github")


def verify_payload_signature(secret: bytes, data: bytes, signature: str) -> bool:
    digest = hmac.new(secret, data, hashlib.sha256).hexdigest()
    sig_parts = signature.split("=", 1)
    if len(sig_parts) < 2 or sig_parts[0] != "sha256" or not hmac.compare_digest(sig_parts[1], digest):
        logger.debug(f"Payload signature {signature} does not match actual digest {digest}")
        return False
    else:
        return True


def github_webhook_parser(request: Request) -> dict:
    event_type = request.headers["X-Github-Event"]
    content_type = request.headers["Content-Type"]
    if content_type == "application/x-www-form-urlencoded":
        payload = json.loads(request.form.to_dict()["payload"])
    elif content_type == "application/json":
        payload = request.get_json()
    else:
        logger.error(f"Invalid content type {content_type}!")
        raise BadRequest(f"Invalid content type {content_type}")

    if payload is None:
        raise BadRequest("Request body must contain JSON!")

    logger.debug(f"Received {event_type} event with payload {payload}")

    repo_config = get_repo_config_by_url(payload["repository"])
    if repo_config is None:
        raise InternalServerError(f'No configuration for repo with URL {payload["repository"]} could be found!')
    secret = repo_config.get("secret", None)
    if secret is None:
        secret = config["secret"]
    secret = secret.encode("utf-8")

    payload_signature = request.headers.get("X-Hub-Signature-256", None)
    if payload_signature is not None:
        if secret is None:
            logger.error("No secret provided in autobuilder config, but received signature from Github!")
            raise InternalServerError("No secret configured!")
        sig_ok = verify_payload_signature(secret, request.data, payload_signature)
        if not sig_ok:
            logger.error("Payload signature failed to verify!")
            raise BadRequest("Payload signature verification failed!")
    return payload
