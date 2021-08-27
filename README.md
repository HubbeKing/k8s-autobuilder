# k8s_autobuilder

A python-based kubernetes-native CI/CD tool.

Runs an API that listens for webhooks and triggers kubernetes jobs based on configured parameters.

This project is still super jank.
Maybe don't use it if you want something stable.

## I make NO PROMISES whether this works yet or not. 
## It probably doesn't, to be honest.

### Configuration
Env vars:
- K8S_AUTOBUILDER_CONFIG: path to a config file for the autobuilder
  - See [examples/config.yaml](examples/config.yaml)
- K8S_AUTOBUILDER_IN_CLUSTER: set to true to use in-cluster config for kubernetes API calls
- K8S_AUTOBUILDER_KUBE_CONFIG: set to true to use a kubeconfig file
  - Make sure to also set KUBE_CONFIG in this case, and of course mount the file as well
- K8S_AUTOBUILDER_MANUAL_KUBE_CONFIG: set to true to manually configure kubernetes API auth
  - If so, use the following env vars to configure:
    - K8S_AUTOBUILDER_KUBE_HOST: kube-apiserver host
    - K8S_AUTOBUILDER_KUBE_VERIFY_SSL: whether or not to verify SSL
    - K8S_AUTOBUILDER_KUBE_SSL_CA_CERT: path to mounted CA SSL cert if verify_ssl is True
    - K8S_AUTOBUILDER_KUBE_TOKEN: bearer token for calls
      - See here to create the token:
      - https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster/

### Job templates:
- See [examples/job_template.yaml](examples/job_template.yaml)
- See [examples/job_template_with_vars.yaml](examples/job_template_with_vars.yaml)

### Job template variables:
- To use variables in a job template, use ${VARIABLE_NAME} syntax
  - For example, `name: foo-${COMMIT_SHA}`
- Variables in a job template can be populated based on data in `config.yaml` in one of three ways:
  - From an env var - the syntax for this is `env.ENV_VAR_NAME`
  - From the webhook payload - the syntax for this is `payload.EVAL_STRING`
    - **Please note that this is trivially abusable - eval() is not even remotely safe for arbitrary user input.**
    - The eval string has the payload dict object pre-pended before eval() is called
      - For example: `payload.[commits[0]["id"]]`
      - This results in an evaluation of `payload[commits[0]["id"]]` - in a Github webhook this is the commit ID of the first commit.
  - With a static string
    - This has no special syntax - `foo`
