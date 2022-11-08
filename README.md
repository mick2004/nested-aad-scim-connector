#  nested-aad-scim-connector
This utility provides ability to sync Users and Groups from AAD to Databricks. This application allows to sync [**nested groups**](https://learn.microsoft.com/en-us/azure/active-directory/fundamentals/how-to-manage-groups#add-or-remove-a-group-from-another-group) and users as well which is not supported in "[Azure Databricks SCIM Provisioning Connector application](https://docs.databricks.com/administration-guide/users-groups/scim/aad.html)"

**Note**: This code is for demonstration purpose only and should not be used as is in Production



## **Steps before running code:**

**Register an application in Azure ADD with ReadAll permissions**

You will need to register an application in Azure Active Directory to enable user [authentication](https://learn.microsoft.com/en-us/graph/auth-v2-user)

Follow the steps below to do same:

1.Open a browser and navigate to the Azure Active Directory admin center and login using a personal account (aka: Microsoft Account) or Work or School Account.

2.Select **Azure Active Directory **in the left-hand navigation, then select **App registrations** under** Manage**.

![image](https://user-images.githubusercontent.com/2042132/200214332-0b686c2d-41df-4b27-863d-c34be789f228.png)

3.Select **New registration**. Enter a name for your application, for example, CustomAADConnector.

4.Set **Supported account types** as desired. 

5.Leave **Redirect URI** empty.

6.Select **Register**. On the application's **Overview page**, copy the value of the** Application (client) ID** and save it, you will need it in the next step. If you chose Accounts in this organizational directory only for Supported account types, also copy the Directory (tenant) ID and save it.





![image](https://user-images.githubusercontent.com/2042132/200214869-afa9efa2-f076-4892-8746-cdeb7a26f7d4.png)

7.Select **Authentication **under Manage. Locate the** Advanced settings** section and change the **Allow public client **flows** toggle to Yes, then choose Save.

![image](https://user-images.githubusercontent.com/2042132/200215091-28962ad9-0767-4914-ad87-37839f24f0a1.png)

8. In the Application menu blade, click on the Certificates & secrets, in the Client secrets section, choose New client secret:

  * Type a key description (for instance app secret)
  
  * Select a key duration as per your security concerns
  
  * The generated key value will be displayed when you click the Add button. Copy the generated value for use in the steps later.
  
  * You'll need this key later in your code's configuration files. This key value will not be displayed again, and is not retrievable by any other means,   so make sure to note it from the Azure portal before navigating to any other screen or blade.
  
9.In the Application menu blade, click on the API permissions in the left to open the page where we add access to the Apis that your application needs.

  * Click the Add a permission button and then,
  
  * Ensure that the Microsoft APIs tab is selected
  
  * In the Commonly used Microsoft APIs section, click on Microsoft Graph
  
  * In the Application permissions section, ensure that the **right permissions are checked: User.Read.All**
  
  * Select the Add permissions button at the bottom.
  
10.At this stage, the permissions are assigned correctly but since the client app does not allow users to interact, the user's themselves cannot consent to these permissions. To get around this problem, we'd let the tenant administrator consent on behalf of all users in the tenant. Click the Grant admin consent for {tenant} button, and then select Yes when you are asked if you want to grant consent for the requested permissions for all account in the tenant. You need to be the tenant admin to be able to carry out this operation.

## Running the app

### As Notebook from your Databricks workspace:

* Go to your workspace and clone this repo.Detailed steps [here](https://learn.microsoft.com/en-us/azure/databricks//repos/git-operations-with-repos) 
* In your repo ,rename config.cfg.template to config.cfg and fill the properties
**Note:** For Prod workloads,its recommended to use Databricks Secrets
* Open the FlattenAndSyncNestedGroups notebook
* Specify Top level group of AAD to sync from 
* Change txtIsDryRun to False if you want to actually create/update users and groups

### As Standalon Python app:
* Clone this repo
* Rename config.cfg.template to config.cfg and fill the properties
* Run FlattenAndSyncNestedGroups.py from PythonEndpoint. 
* pass --dryrun to have a dryrun
* pass top level group as a parameter to python program Ex: python PythonEndpoint/FlattenAndSyncNestedGroups.py parent
Dependency required:
* pip install msgraph-core
* pip install azure-identity
