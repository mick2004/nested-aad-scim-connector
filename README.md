#  nested-aad-scim-connector

<a href="https://pypistats.org/packages/nestedaaddb">
<img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/nestedaaddb?label=PyPi%20Downloads&link=https%3A%2F%2Fpypistats.org%2Fpackages%2Fnestedaaddb">
</a>
<a href="https://pypi.org/project/nestedaaddb/">
<img alt="PyPI" src="https://img.shields.io/pypi/v/nestedaaddb?link=https%3A%2F%2Fpypi.org%2Fproject%2Fnestedaaddb%2F">
</a>



This utility provides ability to sync Users and Groups from AAD to Databricks. This application allows to sync [**nested groups**](https://learn.microsoft.com/en-us/azure/active-directory/fundamentals/how-to-manage-groups#add-or-remove-a-group-from-another-group) and users as well which is not supported in "[Azure Databricks SCIM Provisioning Connector application](https://docs.databricks.com/administration-guide/users-groups/scim/aad.html)"

Using the code is as simple as below few commands :

Install
````
pip install nestedaaddb
````
Configure

Copy the config.cfg.template from here (https://github.com/mick2004/nested-aad-scim-connector/blob/main/config.cfg.template) ,populate details and rename to config.cfg


Usage 
````
from nestedaaddb.nested_groups import SyncNestedGroups
sn = SyncNestedGroups()
sn.loadConfig(<<Path of config.cfg>>")
sn.sync(<<Top level Group>>,<<Is Dry Run>>)
````

## **Details**

## **Steps for running code:**

##  Step (i) 
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


##  Step (i) 
**Populate config.cfg files with Databricks Settings**
Extract the SCIM Token and ACCOUNT SCIM URL Details: https://learn.microsoft.com/en-us/azure/databricks/administration-guide/users-groups/scim/aad#step-1-configure-azure-databricks

![Screenshot 2023-04-24 at 8 17 17 pm](https://user-images.githubusercontent.com/110456615/233968828-ac9ecee3-e996-45c5-8854-e31dfadd5d87.png)



##  Step (iii) 
## Running the app

### As Standalon Python app:
* Install utility via pip

````
pip install nestedaaddb
````

* Copy the config.cfg.template ,populate details and rename to config.cfg
* Run as below:

````
from nestedaaddb.nested_groups import SyncNestedGroups
sn = SyncNestedGroups()
sn.loadConfig(<<Path of config.cfg>>")
sn.sync(<<Top level Group>>,<<Is Dry Run>>)
````

## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
     <td align="center" valign="top" width="14.28%"><a href="https://github.com/jaina15"><img src="https://avatars.githubusercontent.com/u/26425486?v=4?s=100" width="100px;" alt="Shubham Jain"/><br /><sub><b>Shubham Jain</b></sub></a><br /><a href="https://github.com/mick2004/nested-aad-scim-connector/commits?author=jaina15" title="Code">💻</a> <a href="https://github.com/mick2004/nested-aad-scim-connector/commits?author=jaina15" title="Tests">⚠️</a></td>
<td align="center" valign="top" width="14.28%"><a href="https://github.com/AbhiDatabricks"><img src="https://avatars.githubusercontent.com/u/110456615?v=4?s=100" width="100px;" alt="Abhishek Pratap Singh"/><br /><sub><b>Abhishek Pratap Singh</b></sub></a><br /><a href="#infra-AbhiDatabricks" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/mick2004/nested-aad-scim-connector/commits?author=AbhiDatabricks" title="Tests">⚠️</a> <a href="https://github.com/mick2004/nested-aad-scim-connector/commits?author=AbhiDatabricks" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->



