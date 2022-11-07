# AzureAADDatabricksConnector
This utility provides ability to sync Users and Groups from AAD to Databricks. This application allows to sync nested groups and users as well which is not supported in "[Azure Databricks SCIM Provisioning Connector application](https://docs.databricks.com/administration-guide/users-groups/scim/aad.html)"

**Note**: This code is for demonstration purpose only and should not be used as is in Production

**How to run the code:**

**Steps before running code:**

Open a browser and navigate to the Azure Active Directory admin center and login using a personal account (aka: Microsoft Account) or Work or School Account.

Select Azure Active Directory in the left-hand navigation, then select App registrations under Manage.

A screenshot of the App registrations 

Select New registration. Enter a name for your application, for example, Python Graph Tutorial.

Set Supported account types as desired. The options are:

Option	Who can sign in?
Accounts in this organizational directory only	Only users in your Microsoft 365 organization
Accounts in any organizational directory	Users in any Microsoft 365 organization (work or school accounts)
Accounts in any organizational directory ... and personal Microsoft accounts	Users in any Microsoft 365 organization (work or school accounts) and personal Microsoft accounts
Leave Redirect URI empty.

Select Register. On the application's Overview page, copy the value of the Application (client) ID and save it, you will need it in the next step. If you chose Accounts in this organizational directory only for Supported account types, also copy the Directory (tenant) ID and save it.

A screenshot of the application ID of the new app registration

Select Authentication under Manage. Locate the Advanced settings section and change the Allow public client flows toggle to Yes, then choose Save.

A screenshot of the Allow public client flows toggle

From Within Databricks:

1.Go to your workspace and clone this repo.Detailed steps [here](https://learn.microsoft.com/en-us/azure/databricks//repos/git-operations-with-repos) 
2.
