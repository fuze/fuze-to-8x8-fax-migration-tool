import argparse
import os
import time
import requests
import json

# API specific variables
foundry_base_url = "https://api.fuze.com/oss/v1/"
bearer_token = os.environ.get('WARDEN_BEARER_TOKEN')
headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {bearer_token}"
    }
users = []


# Helper class to build and store user data
class User:
    def __init__(self, username=None, user_id=None, service_department_id=None,
                 location_id=None, fax_service_id=None, fax_did=None):
        self.username = username
        self.user_id = user_id
        self.service_department_id = service_department_id
        self.location_id = location_id
        self.fax_service_id = fax_service_id
        self.fax_did = fax_did


# Command line argument setup
def parse_cli_args():
    parser = argparse.ArgumentParser(description="run operations on an organization",  allow_abbrev=False)
    group = parser.add_mutually_exclusive_group()
    parser.add_argument("organization", help="the organization for which to run operations on")
    group.add_argument("-pf", "--print_fax", help="print all existing fax services for the chosen organization",
                    action="store_true")
    group.add_argument("-sf", "--single_fax_id", type=int, help="print user info for a single fax service id")
    group.add_argument("-vfm", "--verbose_full_migration", help="migrates all of an organization's fax services in to "
                                                                "voice DID-Addon services, printing user info for each "
                                                                "service migration", action="store_true")
    group.add_argument("-fm", "--full_migration", help="migrates all of an organization's fax services in to voice "
                                                       "DID-Addon services", action="store_true")
    group.add_argument("-sm", "--single_migration_fax_id", type=int, help="given a single fax service id, migrate to a "
                                                                          "voice DID-Addon service")
    args = parser.parse_args()
    return args


# Purpose: Given a user id, returns the username tied to it
def get_username(u_id):
    users_url = foundry_base_url + "users/"
    u_name_req = requests.get(users_url + u_id, headers=headers)
    u_name_response = u_name_req.json()
    if u_name_req.status_code == 200:
        return u_name_response["data"]["userName"]


# Purpose: Given a fax service id and organization, returns the DID tied to that service
def get_initial_fax_did(service_id):
    extensions_url = foundry_base_url + "extensions/search"
    payload = {
        "filter": {
            "services": [int(service_id)]
        }
    }
    req = requests.post(extensions_url, data=json.dumps(payload), headers=headers)
    response = req.json()
    return response["data"][0]["did"]


# Purpose: Builds objects representing all users with active fax services
# 1) calls /services to gather all active fax services for the org. This returns a user id, department id, location id
# and fax service id for each service
# 2) calls /users in get_username(u_id), taking in the user id from the above call to /services. Returns a username.
# 3) calls /extensions/search in get_initial_fax_did(fax_id) taking in the org and fax id from the above call to
# /services. Returns the DID tied to the service
def get_all_existing_fax_services(org):
    services_url = foundry_base_url + f"services?limit=1000&organization={org}&type=fax&active=true"
    req = requests.get(services_url, headers=headers)
    response = req.json()
    if req.status_code == 200:
        total_active_services = response["pagination"] ["total"]
        services = response["data"]
        print(f"Total Active Fax Services: {total_active_services}")
        for service in services:
            try:
                u_id = service["user"]["id"]
                u_name = get_username(u_id)
            except KeyError:
                u_id = "No user id"
                u_name = "No username"
            dept_id = service["department"]["id"]
            loc_id = service["location"]["id"]
            fax_id = service["id"]
            fax_num = get_initial_fax_did(fax_id)

            users.append(User(username=u_name, user_id=u_id, service_department_id=dept_id,
                              location_id=loc_id, fax_service_id=fax_id, fax_did=fax_num))
    else:
        print("**There was an issue, please try again**")
        print(f"HTTP Response Code: {req.status_code}")
        print(response["msg"])


# Purpose: Builds a single user object given an organization and fax service id
def get_fax_service_by_service_id(org, service_id):
    single_service_url = foundry_base_url + "services/search"
    payload = {
        "filter": {
            "ids": [service_id],
            "types": ["FAX"],
            "organization": org
        }
    }
    req = requests.post(single_service_url, data=json.dumps(payload), headers=headers)
    response = req.json()
    if req.status_code == 200:
        if not response["data"]:
            print(f"There is no existing fax service with service id {service_id}. Please try again...")
        elif response["data"][0]["status"] == "SUSPENDED":
            print(f"The fax service with service id {service_id} is suspended/not active. Please try again...")
        else:
            try:
                u_id = response["data"][0]["user"]["id"]
                u_name = get_username(u_id)
            except KeyError:
                u_id = "No user id"
                u_name = "No username"
            dept_id = response["data"][0]["department"]["id"]
            loc_id = response["data"][0]["location"]["id"]
            fax_num = get_initial_fax_did(service_id)

            users.append(User(username=u_name, user_id=u_id, service_department_id=dept_id,
                              location_id=loc_id, fax_service_id=service_id, fax_did=fax_num))


def deprovision(user):
    deprovision_validation_url = foundry_base_url + "services/deprovision/validation"
    payload = {
        "data": [
            {
                "id": user.fax_service_id,
                "reason": "REDEPLOYMENT"
            }
        ]
    }
    req = requests.post(deprovision_validation_url, data=json.dumps(payload), headers=headers)
    response = req.json()

    if response["data"]["data"][0]["messages"]["errors"]:
        error_msg = response["data"]["data"][0]["messages"]["errors"][0]["message"]
        print(f"Error validating the deprovision: {error_msg}")
    elif response["data"]["data"][0]["messages"]["warnings"]:
        warning_msg = response["data"]["data"][0]["messages"]["warnings"][0]["message"]
        print(f"Warning from validating the deprovision: {warning_msg}")
    elif req.status_code == 200:
        # If deprovision validation was successful, actually deprovision the service using the same payload
        print("Deprovision validation successful. Deprovisioning service...")
        deprovision_url = foundry_base_url + "services/deprovision/"
        req = requests.post(deprovision_url, data=json.dumps(payload), headers=headers)
        response = req.json()

        if req.status_code == 200 or req.status_code == 202:
            print(f"Deprovisioning successful of fax service with DID {user.fax_did}...")
        else:
            print("There was an error deprovisioning the service...Please try again.")


def provision(user, org):
    provision_validation_url = foundry_base_url + "services/provision/validation"

    if user.user_id == "No user id":
        payload = {
            "services": [
                {
                    "organization": org,
                    "did": user.fax_did,
                    "activate": "true",
                    "locationId": user.location_id,
                    "sku": "DID-ADDON-MR-U-1",
                    "departmentId": user.service_department_id
                }
            ]
        }
    else:
        payload = {
            "services": [
                {
                    "organization": org,
                    "did": user.fax_did,
                    "activate": "true",
                    "locationId": user.location_id,
                    "sku": "DID-ADDON-MR-U-1",
                    "user": {
                        "userId": user.user_id
                    },
                    "departmentId": user.service_department_id
                }
            ]
        }

    req = requests.post(provision_validation_url, data=json.dumps(payload), headers=headers)
    response = req.json()

    if response["data"]["services"][0]["messages"]["errors"]:
        error_msg = response["data"]["services"][0]["messages"]["errors"][0]["message"]
        print(f"Error validating the provisioning of DID-Addon service: {error_msg}")
    elif response["data"]["services"][0]["messages"]["warnings"]:
        warning_msg = response["data"]["services"][0]["messages"]["warnings"][0]["message"]
        print(f"Warning from validating the deprovision: {warning_msg}")
    elif req.status_code == 200:
        # If provisionining validation was successful, actually provision the service using the same payload
        print("Provisioning validation successful. Re-provisioning service...")
        provision_url = foundry_base_url + "services/provision/"
        req = requests.post(provision_url, data=json.dumps(payload), headers=headers)
        response = req.json()

        if req.status_code == 200 or req.status_code == 202:
            print(f"Provisioning successful of DID-Addon service with DID {user.fax_did}...")
        else:
            print("There was an error provisioning the service...Please try again.")


# Purpose: Given a user and org, deprovisions their fax service and provisions a DID-Addon service in its place
def migrate_fax_to_voice_service(user_obj, org):
    deprovision(user_obj)
    # deprovision() needs at least 5 seconds to release the DID back in to the pool to be used in provision()
    time.sleep(5)
    provision(user_obj, org)


def main():
    inputs = parse_cli_args() # get all command line arguments for processing
    if inputs.print_fax:
        print(f"Printing all active fax services for {inputs.organization}...")
        get_all_existing_fax_services(inputs.organization)
        if users:
            for user in users:
                print(vars(user))
    elif inputs.single_fax_id:
        print(f"Printing fax service user info for service id {inputs.single_fax_id}...")
        get_fax_service_by_service_id(inputs.organization, inputs.single_fax_id)
        if users:
            print(vars(users[0]))
    elif inputs.verbose_full_migration:
        print(f"Migrating all {inputs.organization} fax services to DID-Addon voice services")
        get_all_existing_fax_services(inputs.organization)
        if users:
            for user in users:
                print(f"\nUsername: {user.username}")
                print(f"User ID: {user.user_id}")
                print(f"Service Department ID: {user.service_department_id}")
                print(f"Location ID: {user.location_id}")
                print(f"Fax Service ID: {user.fax_service_id}")
                print(f"Fax DID: {user.fax_did}")
                print("**-----------------------------------**")
                migrate_fax_to_voice_service(user, inputs.organization)
    elif inputs.full_migration:
        print(f"Migrating all {inputs.organization} fax services to DID-Addon voice services")
        get_all_existing_fax_services(inputs.organization)
        if users:
            for user in users:
                migrate_fax_to_voice_service(user, inputs.organization)
    elif inputs.single_migration_fax_id:
        print("Migrating the following user:\n")
        get_fax_service_by_service_id(inputs.organization, inputs.single_migration_fax_id)
        if users:
            print(f"Username: {users[0].username}")
            print(f"User ID: {users[0].user_id}")
            print(f"Service Department ID: {users[0].service_department_id}")
            print(f"Location ID: {users[0].location_id}")
            print(f"Fax Service ID: {users[0].fax_service_id}")
            print(f"Fax DID: {users[0].fax_did}")
            print("**-----------------------------------**")
            migrate_fax_to_voice_service(users[0], inputs.organization)


if __name__ == '__main__':
    main()




