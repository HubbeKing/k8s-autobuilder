from datetime import datetime
from flask import Flask, jsonify, request
import jq
import logging
import os
import yaml
from werkzeug.exceptions import BadRequest, InternalServerError

from backend.generics import config, load_config, get_repo_config_by_name, get_repo_config_by_url, setup_logging
from backend.webhooks.github import github_webhook_parser
from backend.kubernetes_interface import create_job, list_repo_jobs

app = Flask(__name__)
setup_logging()
load_config()
logger = logging.getLogger("k8s_autobuilder.backend")



# TODO "API" endpoints to tie in a frontend
# TODO Job logs persistence
# TODO Repo status persistence
# TODO /metrics endpoint


@app.route("/healthz")
def healthcheck():
    return 'OK', 200


@app.route("/webhook_listener", methods=["POST"])
def webhook_listener():
    # TODO support for non-github webooks (curl, gitea, etc)
    if "X-Github-Event" in request.headers:
        logger.info("Received GitHub webhook. Parsing...")
        try:
            payload = github_webhook_parser(request)
        except BadRequest as e:
            return e.description, 400
        except InternalServerError as e:
            return e.description, 500
        event_type = payload["X-Github-Event"]
        repository_url = payload["repository"]
    else:
        return "Unknown webhook received.", 400

    repo_config = get_repo_config_by_url(repository_url)
    valid_hooks = [hook for hook in repo_config["hooks"] if hook["event_type"] == event_type]
    for hook in valid_hooks:
        variables = hook["template_vars"]
        populated_vars = {}
        for var in variables:
            if "value" in var:
                # populate with raw value
                populated_vars[var["name"]] = str(var["value"])
            else:
                # valueFrom
                if "env" in var["valueFrom"]:
                    # populate with env var
                    populated_vars[var["name"]] = os.environ.get(var["valueFrom"]["env"])
                elif "jq" in var["valueFrom"]:
                    # populate using jq program using payload as the input
                    try:
                        populated_vars[var["name"]] = jq.compile(var["valueFrom"]["jq"]).input(payload).first()
                    except Exception:
                        # skip to next hook, we cannot be certain this hook won't break things
                        logger.exception("Exception during jq compilation!")
                        break
                else:
                    populated_vars[var["name"]] = ""

        logger.debug(f"Populated vars for job template - {populated_vars}")

        job_template_path = hook["job_template"]
        job_namespace = hook["namespace"] if "namespace" in hook else config["namespace"]
        logger.info(f"Creating job for repository {repository_url} in namespace {job_namespace} using template file {job_template_path}")
        with open(job_template_path) as job_template_file:
            job_template_string = job_template_file.read()
            logger.debug(f"Loaded job template - {job_template_string}")
            for name, value in populated_vars.items():
                job_template_string.replace(name, value)
        logger.debug(f"Populated job template - {job_template_string}")
        job = yaml.safe_load(job_template_string)

        # add autobuilder identifying labels to job so we can easily find it later
        job["metadata"]["labels"]["hubbeking.k8s.autobuilder/repo_name"] = repo_config["name"]
        job["metadata"]["labels"]["hubbeking.k8s.autobuilder/build_date"] = datetime.utcnow().isoformat()
        # TODO add Finalizer to job so it isn't deleted until autobuilder has retrieved its logs and status and stored them?
        job = create_job(job_namespace, job)
        if job is not None:
            logger.debug(f"Job creation raw result - {job}")
            job_name = job.metadata.name
            logger.info(f"Created job {job_name} for repository {repository_url} in namespace {job_namespace}")
            # TODO store job name, poll for job result, store job logs and job result
        else:
            logger.error(f"Failed to create job for repository {repository_url} in namespace {job_namespace}")
    # If we get here, the webhook has been handled to the best of our ability.
    return jsonify({"msg": "Received"})
