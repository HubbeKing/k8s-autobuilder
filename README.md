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
  - Make sure to also set KUBECONFIG in this case, and of course mount the file as well
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
  - With a static value:
      ```
      - name: IMAGE_TAG
        value: "latest"
      ```
  - With an env var:
    ```
    - name: KEY_PATH
      valueFrom:
        env: KEY_PATH
    ```
  - Using a jq program - note that the webhook payload will be given as the input.
    ```
    - name: COMMIT_SHA
      valueFrom:
        jq: '.commits[0]["id"]'
    ```
