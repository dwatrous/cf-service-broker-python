import bottle
import requests
import json
import os

# constant representing the API version supported
# keys off HEADER X-Broker-Api-Version from Cloud Controller
X_BROKER_API_VERSION = 2.3
X_BROKER_API_VERSION_NAME = 'X-Broker-Api-Version'

# UPDATE THIS FOR YOUR ECHO SERVICE DEPLOYMENT
service_base = "localhost"

# service endpoint templates
service_instance = "http://"+service_base+"/echo/{{instance_id}}"
service_binding = "http://"+service_base+"/echo/{{instance_id}}/{{binding_id}}"
service_dashboard = "http://"+service_base+"/echo/dashboard/{{instance_id}}"

# plans
big_plan = {
          "id": "big_0001",
          "name": "large",
          "description": "A large dedicated service with a big storage quota, lots of RAM, and many connections",
          "free": False
        }

small_plan = {
          "id": "small_0001",
          "name": "small",
          "description": "A small shared service with a small storage quota and few connections"
        }

# dashboard
dashboard_details = {
          "id": "client-id-1",
          "secret": "secret-1",
          "redirect_uri": "http://"+service_base+"/echo/dashboard"
        }

# services
echo_service = {'id': 'echo_service', 'name': 'Echo Service', 'description': 'Echo back the value received', 'bindable': True, 'plans': [big_plan], 'dashboard_client': dashboard_details}

invert_service = {'id': 'invert_service', 'name': 'Invert Service', 'description': 'Invert the value received', 'bindable': True, 'plans': [small_plan], 'dashboard_client': None}


@bottle.error(401)
@bottle.error(409)
def error(error):
    bottle.response.content_type = 'application/json'
    return '{"error": "%s"}' % error.body

def authenticate(username, password):
    return True

@bottle.route('/v2/catalog', method='GET')
@bottle.auth_basic(authenticate)
def catalog():
    """
    Return the catalog of services handled
    by this broker

    GET /v2/catalog:

    HEADER:
        X-Broker-Api-Version: <version>

    return:
        JSON document with details about the
        services offered through this broker
    """
    api_version = bottle.request.headers.get('X-Broker-Api-Version')
    if not api_version or float(api_version) < X_BROKER_API_VERSION:
        bottle.abort(409, "Missing or incompatible %s. Expecting version %0.1f or later" % (X_BROKER_API_VERSION_NAME, X_BROKER_API_VERSION))
    return {"services": [echo_service, invert_service]}


@bottle.route('/v2/service_instances/<instance_id>', method='PUT')
@bottle.auth_basic(authenticate)
def provision(instance_id):
    """
    Provision an instance of this service
    for the given org and space

    PUT /v2/service_instances/<instance_id>:
        <instance_id> is provided by the Cloud
          Controller and will be used for future
          requests to bind, unbind and deprovision

    BODY:
        {
          "service_id":        "<service-guid>",
          "plan_id":           "<plan-guid>",
          "organization_guid": "<org-guid>",
          "space_guid":        "<space-guid>"
        }

    return:
        JSON document with details about the
        services offered through this broker
    """
    if bottle.request.content_type != 'application/json':
        bottle.abort(415, 'Unsupported Content-Type: expecting application/json')
    # get the JSON document in the BODY
    provision_details = bottle.request.json
    # provision the service
    provision_result = requests.put(bottle.template(service_instance, instance_id=instance_id))
    # TODO: it may make sense for the broker to associate the new instance with service/plan/org/space
    # check for case of already provisioned service
    if provision_result.status_code == 409:
        # in this case return empty document with 200
        # in cases where the service must be provisioned uniquely, pass along the 409
        return {}
    if provision_result.status_code == 200:
        # return created status code
        bottle.response.status = 201
        return {"dashboard_url": bottle.template(service_dashboard, instance_id=instance_id)}

@bottle.route('/v2/service_instances/<instance_id>', method='DELETE')
@bottle.auth_basic(authenticate)
def deprovision(instance_id):
    """
    Deprovision an existing instance of this service

    DELETE /v2/service_instances/<instance_id>:
        <instance_id> is the Cloud Controller provided
          value used to provision the instance

    return:
        As of API 2.3, an empty JSON document
        is expected
    """
    # deprovision service
    deprovision_result = requests.delete(bottle.template(service_instance, instance_id=instance_id))
    # check for case of no existing service
    if deprovision_result.status_code == 404:
        bottle.response.status = 410
    # send response
    return {}

@bottle.route('/v2/service_instances/<instance_id>/service_bindings/<binding_id>', method='PUT')
@bottle.auth_basic(authenticate)
def bind(instance_id, binding_id):
    """
    Bind an existing instance with the
    for the given org and space

    PUT /v2/service_instances/<instance_id>/service_bindings/<binding_id>:
        <instance_id> is the Cloud Controller provided
          value used to provision the instance
        <binding_id> is provided by the Cloud Controller
          and will be used for future unbind requests

    BODY:
        {
          "plan_id":           "<plan-guid>",
          "service_id":        "<service-guid>",
          "app_guid":          "<app-guid>"
        }

    return:
        JSON document with credentails and access details
        for the service based on this binding
        http://docs.cloudfoundry.org/services/binding-credentials.html
    """
    if bottle.request.content_type != 'application/json':
        bottle.abort(415, 'Unsupported Content-Type: expecting application/json')
    # get the JSON document in the BODY
    binding_details = bottle.request.json
    # bind the service
    binding_result = requests.put(bottle.template(service_binding, instance_id=instance_id, binding_id=binding_id))
    # TODO: it may make sense for the broker to associate the new instance with service/plan/app
    # check for case of already provisioned service
    if binding_result.status_code == 409:
        bottle.response.status = 409
        return {}
    if binding_result.status_code == 200:
        # return created status code
        bottle.response.status = 201
        return {"credentials": {"uri": bottle.template(service_binding, instance_id=instance_id, binding_id=binding_id)}}

@bottle.route('/v2/service_instances/<instance_id>/service_bindings/<binding_id>', method='DELETE')
@bottle.auth_basic(authenticate)
def unbind(instance_id, binding_id):
    """
    Unbind an existing instance associated
    with the binding_id provided

    DELETE /v2/service_instances/<instance_id>/service_bindings/<binding_id>:
        <instance_id> is the Cloud Controller provided
          value used to provision the instance
        <binding_id> is the Cloud Controller provided
          value used to bind the instance

    return:
        As of API 2.3, an empty JSON document
        is expected
    """
    # unbind the service
    unbinding_result = requests.delete(bottle.template(service_binding, instance_id=instance_id, binding_id=binding_id))
    # check for case of no existing service
    if unbinding_result.status_code == 404:
        bottle.response.status = 410
    # send response
    return {}

if __name__ == '__main__':
    port = int(os.getenv('PORT', '8080'))
    bottle.run(host='0.0.0.0', port=port, debug=True, reloader=False)