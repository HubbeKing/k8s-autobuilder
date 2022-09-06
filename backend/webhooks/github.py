from flask import Request
import hashlib
import hmac
import json
import logging
from werkzeug.exceptions import BadRequest, InternalServerError

from backend.kubernetes_interface import get_autobuilder_repo_config_by_url, get_secret_string

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

    repo_config = get_autobuilder_repo_config_by_url(payload["repository"])
    if repo_config is None:
        raise InternalServerError(f'No configuration for repo with URL {payload["repository"]} could be found!')
    webhook_secret_config = repo_config["webhookSecret"]
    if webhook_secret_config is None:
        logger.error(f"No webhookSecret in repository configuration for {repo_config['repository']['name']}")
        raise InternalServerError(f"Configuration for repo {repo_config['repository']['name']} is invalid!")
    # retrieve secret from cluster
    secret = get_secret_string(webhook_secret_config["namespace"], webhook_secret_config["name"], webhook_secret_config["key"])
    secret = secret.encode("utf-8")  # turn secret into bytes, as needed for verifying signature

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
