# Azure DevOps CI/CD Pipelines Guide

## Introduction

This guide is to be used in conjuction with `docs/azure-app-service.md`. While this guide can be executed first, it will be easier to first set up the Azure App Services as certain environment variables and settings will be required for the pipelines steps below.

The Azure DevOps Pipelines are a two-pronged approach to deployment: Continuous Integration (CI) followed by Continued Deployment (CD). In layman's terms this means that the CI pipeline will ensure that the latest build passes a series of business-specific prerequisites and tests, after which the CD pipeline handles deploying the application to the appropriate App Service. There is one universal CI pipeline for the three branches `develop`, `test`, `uat` and their respective App Services, however an individual CD pipeline exists ber branch.

Pipelines are housed under Azure's DevOps offering and can be accessed via https://dev.azure.com. Both the CI and CD pipelines' settings and implementation details can be found by navigating to **Pipelines -> Pipelines**. 

## CI Pipeline

The CI Pipeline is a universal pipeline that upon succesful completion, triggers the branch-specific CD pipeline. At the time of writing this document, the CI pipeline is named `pac-backend-CI` and the YAML file is housed at the project root directy as `azure-pipelines.yml`. 

If the `pac-backend-CI` pipeline already exists, that means the application's BitBucket repository is currently connected with the CI pipeline, however the steps to replicate this state are as follows:

1. Go to https://dev.azure.com
2. Navigate to **Pipelines -> Pipelines**
3. Click **New Pipeline**
4. Under the **Connect** step, select **BitBucket Cloud**
5. Under the **Select** step, select the backend repository (`internetdev/pac-new-backend` at the time of writing) 
6. Under the **Configure** step, select **Existing Azure Pipelines YAML file**. Select **Branch** `develop`, and **Path** `azure-pipelines.yml`
7. Confirm completion
8. Under the newly created pipeline's settings, set the same environment variable names as required for the `develop` settings file under `pac/settings/azure.py` so that the CI pipeline's environment can properly establish a connection to the database resources.
9. Set environemnt variable `DJANGO_SETTINGS_MODULE = pac.settings.azure`, this ensures that the develop branch's settings file is used for connecting to the database's develop instance for running the necessary CI steps such as test cases and validations. For more information regarding environemnt variables, branches, and settings files, please read `docs/azure-app-service.md`
    
If the steps above executed succesfully, the CI pipeline should now be triggered each time a push is made to the remote BitBucket backend repository's `develop`, `test`, or `uat` branches.


## CD Pipeline

Now that the CI Pipeline is hopefully up and running, the CD pipeline needs to be triggered to rebuild and redeploy the web application hosted on Azure App Service with the latest changes. Each branch maps to a different CD pipeline, and at the time of writing this document, the branches have the following mapping with the pipelines and their respective YAML files housed at the project root directory.

| Branch    | Pipeline              | YAML                    | Azure App Service    |
| --------- | --------------------- | ----------------------- | -------------------- |
| `develop` | `pac-backend-dev-CD`  | `azure-deploy.yml`      | `drpac-backend`      |
| `test`    | `pac-backend-test-CD` | `azure-deploy-test.yml` | `drpac-backend-test` |
| `uat`     | `pac-backend-uat-CD`  | `azure-deploy-uat.yml`  | `drpac-backend-uat`  |

If the pipelines already exist, that means the application's BitBucket reposity is currently connected with the CD pipelines and the pipelines are being triggered following a succesful run of the CI pipeline, however the steps to replicate this state are described below. Remember they must be completed for each of the branches `develop`, `test`, and `uat`. 

1. Follow steps 1 - 5 from the **CI Pipeline** section above
2. Under the **Configure** step, select **Existing Azure Pipelines YAML file**. For **Branch** select **Branch** from the table above, and for **Path** select the appropriate **YAML**
3. Confirm completion
4. Under the newly created pipeline's settings, set the environment variables `DEPLOYMENT_PASSWORD`, `DEPLOYMENT_USERNAME`, and `X_DEPLOYMENT_URL` where `X` is the name of the branch in all caps. These are the **deployment credentials** set-up when following `docs/azure-app-service.md` and are needed to push the latest changes to the Azure App Service's remote Git.
5. Navigagte to the pipeline's **Triggers**
6. Under **Continuos integration**, select **Disable continuous integration**
7. Under **Pull request validation**, select **Disable pull request validation**
8. Under **Build completion**
   1. Select the backend CI pipeline created in the previous section for **Triggering build**
   2. Add **Branch filters**, include the current branch and exclude the two other branches. As an example, if the current CD pipeline is being set-up for the `develop` branch, add an *Include* branch filter for `develop` and two *Exclude* branch filters - one for `test` and the other for `uat`
   
If the steps above executed succesfully for each branch, the three CD pipelines should now be triggered each time the CI pipeline succesfully executes following a push to the remote Bitbucket backend repository's `develop`, `test`, or `uat` branches.