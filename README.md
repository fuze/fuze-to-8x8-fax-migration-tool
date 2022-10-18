# Fuze to 8x8 Fax Service Migration Tool

### Description
The purpose of this tool is to help migrate Fuze fax services in to Fuze DID-addon services in bulk. 
This is because current Fuze infrastructure supports redirecting voice services to 8x8, but not e-fax services. T.38
signaling should still work as expected. Once the services have been converted, we can redirect inbound fax traffic to those 
DID's from the PSTN over to 8x8 on our SIP trunks. While the services are now voice SKU's on the Fuze end, they will 
continue to be used as fax services on the 8x8 end, while Fuze remains the RESPORG of the DID's.

### Foundry API
This project utilizes the Foundry API, which is actually an internal set of various API's used for a multitude of 
reasons. In this case, it will be used to assist with bulk deprovisioning of fax services and their subsequent 
reprovisioning in to DID-addon services. In order to use this API, you must have a Bearer token generated through 
the Warden service. There are other underlying user permissions as well which are outside the scope of this document 
for now. 

**Wiki for API:** https://wiki.fuze.global/display/QA/Bulk+Provision+via+API#BulkProvisionviaAPI-GETor%22list%22endpoints

**Swagger:** https://swagger.foundry-stage.fuze.com/

### Examples 
**How to Run**
```commandline
Add more here when all options are in place
```
**Getting all active fax services for an organization**
```commandline
(venv) PS C:\Users\jdiamond\Desktop\GitHub\fuze-to-8x8-fax-migration-tool> python .\app.py cr3testhamid --print_fax
```
```commandline
Printing all active fax services for cr3testhamid...
Total Active Fax Services: 5
{'username': 'faxapitest1.cr3testprod', 'user_id': '341162968294265701', 'service_department_id': '25206', 'location_id': '18788', 'fax_service_id': '2758418', 'fax_did': '+14139984132'}
{'username': 'faxapitest2.cr3testprod', 'user_id': '319936644795824310', 'service_department_id': '25206', 'location_id': '18788', 'fax_service_id': '2758419', 'fax_did': '+15083132025'}
{'username': 'No username', 'user_id': 'No user id', 'service_department_id': '25206', 'location_id': '18788', 'fax_service_id': '2758420', 'fax_did': '+15084080099'}
{'username': 'faxapitest4.cr3testprod', 'user_id': '374579206337483553', 'service_department_id': '25206', 'location_id': '18788', 'fax_service_id': '2758421', 'fax_did': '+16172452522'} 
{'username': 'faxapitest5.cr3testprod', 'user_id': '427856568234504789', 'service_department_id': '25206', 'location_id': '18788', 'fax_service_id': '2758424', 'fax_did': '+16172452523'}
```
**Get info on a single fax service (knowing its service id)**
```commandline
(venv) PS C:\Users\jdiamond\Desktop\GitHub\fuze-to-8x8-fax-migration-tool> python .\app.py cr3testhamid --single_fax_id 2758421
```
```commandline
{'username': 'faxapitest4.cr3testprod', 'user_id': '374579206337483553', 'service_department_id': '25206', 'location_id': '18788', 'fax_service_id': 2758421, 'fax_did': '+16172452522'}
```
**Trying to check a non-existent fax service**
```commandline
(venv) PS C:\Users\jdiamond\Desktop\GitHub\fuze-to-8x8-fax-migration-tool> python .\app.py cr3testhamid --single_fax_id 1111111111111
```
```commandline
Printing fax service user info for service id 1111111111111...
There is no existing fax service with service id 1111111111111.Please try again...
```
**Trying to check a suspended fax service**
```commandline
(venv) PS C:\Users\jdiamond\Desktop\GitHub\fuze-to-8x8-fax-migration-tool> python .\app.py cr3testhamid --single_fax_id 2758418
```
```
Printing fax service user info for service id 2758418...
The fax service with service id 2758418 is suspended/not active.Please try again...
```
**You can't check all of an org's faxes and also check a single fax service in the same command**
```commandline
(venv) PS C:\Users\jdiamond\Desktop\GitHub\fuze-to-8x8-fax-migration-tool> python .\app.py cr3testhamid --print_fax --single_fax_id 2758421
```
```commandline
usage: app.py [-h] [-pf | -sf SINGLE_FAX_ID] organization
app.py: error: argument -sf/--single_fax_id: not allowed with argument -pf/--print_fax
```

### Running the Project Locally
**Get a Warden token**

A token represents a Fuze user account with the correct permissions to run various services on the Fuze platform. Here it
is needed to interact and authenticate with the Foundry API. 

See 'Windows' or 'Mac' sections of this wiki: https://wiki.fuze.global/display/SUPPORTKB/How-to+Generate+a+Bearer+Token+for+SCIM+API


**Create a virtual environment**

Add a Warden Bearer token to an environment variable called "WARDEN_BEARER_TOKEN". Where this is stored is different
depending on which local terminal you are using. You will need this in order to authenticate to the Foundry API

See: https://www.roelpeters.be/set-environment-variables-in-virtual-environment-python/

**Ex.** Unix: ```export WARDEN_BEARER_TOKEN="2.XXXXX"``` (activate)

**Ex.** Windows: ```set WARDEN_BEARER_TOKEN="2.XXXXX"``` (activate.bat)

**Ex.** Powerhsell: `````$env:WARDEN_BEARER_TOKEN  = '2.XXX'````` (Activate.ps1)

**Dependencies**

All modules and packages used are part of Python's standard library so there should not be any need to install anything 
in your virtual environment. If for some reason you are missing any of the dependencies, you can run the following 
command to install the dependencies in your virtual environment:
```commandline
pip install -r requirements. txt
```