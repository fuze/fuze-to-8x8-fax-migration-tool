# Fuze to 8x8 Fax Service Migration Tool

###Description
The purpose of this tool is to help migrate Fuze fax services in to Fuze DID-addon services in bulk.
Once the services have been converted, we can redirect inbound traffic to those DID's from the PSTN over to 8x8 on
our SIP trunks. While the services are now voice SKU's on the Fuze end, they will continue to be used as fax services
on the 8x8 end, while Fuze remains the RESPORG of the DID's.

###Foundry API
This project utilizes the Foundry API, which is actually an internal set of various API's used for a multitude of 
reasons. In this case, it will be used to assist with bulk deprovisioning of fax services and their subsequent 
reprovisioning in to DID-addon services. In order to use this API, you must have a Bearer token generated through 
the Warden service. There are other underlying user permissions as well which are outside the scope of this document 
for now. 

**Wiki for API:** https://wiki.fuze.global/display/QA/Bulk+Provision+via+API#BulkProvisionviaAPI-GETor%22list%22endpoints

**Swagger:** https://swagger.foundry-stage.fuze.com/

###Running the Project Locally
TODO