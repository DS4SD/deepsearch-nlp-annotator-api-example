## Deploying the application

### Running in Kubernetes / Openshift

The repository contains a Helm Chart in [./chart](./chart) which can be used to deploy and expose the application from a Kubernetes cluster.

### Running in Serverless environments

### Prerequisites

- You must have an IBM Cloud account. If you don't have one, [sign up for a trial](https://cloud.ibm.com/registration?cm_mmc=IBMBluemixGarageMethod-_-MethodSite-_-10-19-15::12-31-18-_-bm_reg). The account requires an IBMid. If you don't have an IBMid, you can create one when you register.
- A GitHub account. If you don't have one, [sign up](https://github.com/).
- Verify the [toolchains and tool integrations that are available](https://cloud.ibm.com/docs/ContinuousDelivery?topic=ContinuousDelivery-cd_about) in your region and IBM Cloud environment. A toolchain is a set of tool integrations that support development, deployment, and operations tasks.

**Option 1:**

Deploy to IBM Cloud using [IBM Code Engine](https://www.ibm.com/cloud/code-engine) platform (a Knative distribution)

- Open the [Code Engine](https://cloud.ibm.com/codeengine/overview) console.
- Select **Start creating** from **Start with source code.**
- Select **Application.**
- Enter a name for the application. Use a name for your application that is unique within the project.
- Select a project from the list of available projects. You can also [create a new one](https://cloud.ibm.com/docs/codeengine?topic=codeengine-manage-project#create-a-project). Note that you must have a selected project to deploy an app.
- Select **Source code.**
- Click **Specify build details.**
- Select `https://github.com/IBM/deepsearch-nlp-annotator-api-example` for Source repository and `master` for Branch name. Note that if you do not provide a branch name and you leave the field empty, Code Engine automatically determines the branch name. Click **Next.**
- Select `Dockerfile` for Strategy, `Dockerfile` for Dockerfile, `10m` for Timeout, and `Medium` for Build resources. Click **Next.**
- Select a container registry location, such as `IBM Registry, Dallas`.
- Select `Automatic` for **Registry access.**
- Select an existing namespace or enter a name for a new one, for example, `newnamespace`.
- Enter a name for your image and optionally a tag.
- Click **Done.**
- Click **Create.**

Documentation: https://cloud.ibm.com/docs/codeengine

**Option 2:**

Deploy to IBM Cloud using a preconfigured devops toolchain button

The Deploy to IBM Cloud button is an efficient way to share your public Git-sourced app so that other people can experiment with the code and deploy it to IBM Cloud by using a toolchain. Anyone who clicks the button creates a cloned copy of the code in a new Git repository (repo) so that your original app remains unaffected.

To get started, click **Deploy to IBM Cloud**.

[![Deploy to IBM Cloud](https://cloud.ibm.com/devops/setup/deploy/button.png)](https://cloud.ibm.com/devops/setup/deploy?repository=https%3A//github.com/IBM/deepsearch-nlp-annotator-api-example)

### Configuration

Following the steps above will deploy the model with default settings. It is highly recommended to customize the model configuration, in particular using a non-trivial API key.

1. Open the Code Engine configuation of the model and click on "Edit and create new revision"
2. Select the tab "Environment variables"
![cps](.readme_resources/code-engine-env-1.png)

3. Add a new environment variable
  - Name: `auth`
  - Value: something like `{"api_key": "super-secret-key-123"}`, where you replace `super-secret-key-123` with your own secret.
<img src='.readme_resources/code-engine-env-2.png' width='250'>

4. Confirm the new variable and save the new Code Engine configuration.


