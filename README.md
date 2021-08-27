# k8s_autobuilder

A python-based kubernetes-native CI/CD tool.

Runs an API that listens for webhooks and triggers kubernetes jobs based on configured parameters.

This project is still super jank.
Maybe don't use it if you want something stable.

## Configuration
Env vars:
- K8S_AUTOBUILDER_CONFIG: path to a config file for the autobuilder
  - See [examples/config.yaml]

Job templates:
- See [examples/job_template.yaml] and [examples/job_template_with_vars.yaml]

Job template variables:
- To use variables in a job template, use ${VARIABLE_NAME} syntax
  - For example, `name: foo-${COMMIT_SHA}`
- Variables in a job template can be populated based on data in `config.yaml` in one of three ways:
  - From an env var - the syntax for this is `env.ENV_VAR_NAME`
  - From the webhook payload - the syntax for this is `payload.EVAL_STRING`
    - Please note that this is trivially abusable - eval() is not even remotely safe for arbitrary user input.
    - The eval string has the payload dict object pre-pended before eval() is called
      - For example: `payload.[commits[0]["id"]]`
      - This results in an evaluation of `payload[commits[0]["id"]]` - in a Github webhook this is the commit ID of the first commit.
  - With a static string
    - This has no special syntax - `foo`
