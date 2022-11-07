# AzureAADDatabricksConnector
This utility provides ability to sync Users and Groups from AAD to Databricks. This application allows to sync [**nested groups**](https://learn.microsoft.com/en-us/azure/active-directory/fundamentals/how-to-manage-groups#add-or-remove-a-group-from-another-group) and users as well which is not supported in "[Azure Databricks SCIM Provisioning Connector application](https://docs.databricks.com/administration-guide/users-groups/scim/aad.html)"

**Note**: This code is for demonstration purpose only and should not be used as is in Production



**Steps before running code:**

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


From Within Databricks:

1.Go to your workspace and clone this repo.Detailed steps [here](https://learn.microsoft.com/en-us/azure/databricks//repos/git-operations-with-repos) 
2.
