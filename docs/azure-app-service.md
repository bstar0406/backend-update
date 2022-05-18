# Azure App Service Deployment Guide

## Introduction

This guide is to be used in conjuction with `docs/azure-pipelines.md`. 

Deployment on Azure App Service is relatively straightforward and is best handled directly via the resource portal on http://portal.azure.com. Azure App Service builds a virtual environment based on our application's settings and then hosts it as a web application. There are three different App Services for the back-end, each assosciated with a respective branch.

| Branch    | Azure App Service    |
| --------- | -------------------- |
| `develop` | `drpac-backend`      |
| `test`    | `drpac-backend-test` |
| `uat`     | `drpac-backend-uat`  |

For each App Service, the set up process is identical aside from the environment variables. 

## Steps
The following steps can be skipped if the App Services named `drpac-backend`, `drpac-backend-test`, and `drpac-backend-uat` are already available on the Azure Portal. However recreating any of the App Services can be done by following these steps:

1. Navigate to **Deployment -> Deployment Center**
2. Under the **SOURCE CONTROL** step and **Continuous Deployment (CI / CD)** category, select **Local Git** and click Continue
3. Under the **BUILD PROVIDER** step, select **App Service build service** and click Continue
4. Under **SUMMARY** category, click Finish
5. Navigate to **Settings -> Configuration -> General settings** and select...
   1. **Stack** Python
   2. **Major Version** 3.7
   3. **Minor Version** 3.7
   
NOTE: Check out https://docs.microsoft.com/en-us/azure/app-service/containers/how-to-configure-python for more information regarding how App Service handles Python applications + custom startup scripts.

The Deloyment Center splash page should now be rendered along with a URI under the `Git Clone Uri` title. This URI will be required by CD Pipeline to ensure that each time a `git push` is made to the branch assosciated with the App Service, the App Service is also pushed to, built, and updated.

## Deployment Credentials
Along with the `Git Clone Uri` mentioned above, deployment credentials need to be set-up so that the CD Pipeline can properly `git push` to the App Service. In order to do this, click the **Deployment Credentials** header and navigate to **User Credentials** under **Scope**.
Set a `username` and `password` and keep note of it along with the `Git Clone Uri`.

## Environment Variables
Environemnt variables are the fork in the road that seperate the different App Services from each other. This makes sense since `develop`, `test`, and `uat` all reference different databases and settings files, consequently requiring different enviroment variables to orchestrate this. The base settings file located at pac/settings/settings.py is identical for each branch, however custom branch settings files have the following paths;

| Branch    | Path                         | Azure App Service    |
| --------- | ---------------------------- | -------------------- |
| `develop` | `pac/settings/azure.py`      | `drpac-backend`      |
| `test`    | `pac/settings/azure-test.py` | `drpac-backend-test` |
| `uat`     | `pac/settings/azure-uat.py`  | `drpac-backend-uat`  |

In order for the App Service to be able to pick-up the appropriate settings file, Django uses an environment variable called `DJANGO_SETTINGS_MODULE` that points to the relavent settings file in Python path syntax. As an example, the `develop` branch App Service called `drpac-backend` should have `DJANGO_SETTINGS_MODULE = pac.settings.azure`. For more information regarding this, please have a look at the following: https://docs.djangoproject.com/en/2.1/topics/settings/#designating-the-settings. 

In addition to this, the App Service needs other environemnt variables to be declared so that the Django settings files reference the correct databases depending on the branch. Since each branch has different environemnt variables, have a look at any of the settings files mapped above to get the names of the variables needed for each relavent branch. 

Once ready, navigate to **Settings -> Configuration**, and for each required environment variable, click **New application setting** and fill in the details. Repeat this process for `develop`, `test`, and `uat`, but be sure to check the appropriate settings file to gather the correct environment variable names. If new variable names are desired, make sure they are named consistently across the settings files, the App Service, and the local developement environemnt.

## Next Steps

In order to trigger changes to the App Service hosted web application following a pushes to our remote repository, follow the steps in `docs/azure-pipelines.md` for a full CI/CD integration.

