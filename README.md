# k8s_autobuilder

A simplistic Python-based kubernetes-native CI/CD tool.

Runs an API that listens for webhooks and triggers kubernetes jobs based on templates.

- This project is still very early Alpha, and does not yet work.
- CRD specs have been thought up, but not written down as CRD manifests.
- Nor has the support for reading CRDs been actually added to the backend.

### Configuration
Environment variables for kube-apiserver authentication:
- K8S_AUTOBUILDER_IN_CLUSTER: set to true to use in-cluster config for kubernetes API calls
- K8S_AUTOBUILDER_KUBE_CONFIG: set to true to use a kubeconfig file
  - Make sure to also set KUBECONFIG in this case, and of course mount the file as well
- K8S_AUTOBUILDER_MANUAL_KUBE_CONFIG: set to true to manually configure kubernetes API auth
  - If so, use the following env vars to configure:
    - K8S_AUTOBUILDER_KUBE_HOST: kube-apiserver host
    - K8S_AUTOBUILDER_KUBE_VERIFY_SSL: whether to verify SSL
    - K8S_AUTOBUILDER_KUBE_SSL_CA_CERT: path to mounted CA SSL cert if verify_ssl is True
    - K8S_AUTOBUILDER_KUBE_TOKEN: bearer token for calls
      - See here to create the token:
      - https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster/

### CRDs
For configuration of projects to build / webhooks to answer, we use CRD objects stored in the cluster.

#### Repository configuration
- See [examples/repo_config.yaml](examples/repo_config.yaml)

#### Job template
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
  - With an env var - note that these are populated using the autobuilder's environment:
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
