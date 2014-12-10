CloudFoundry Service Broker v2 implementation in Python
========================

CloudFoundry (and Stackato and HP Helion Development Platform) provide a [Service Broker API](http://docs.cloudfoundry.org/services/api.html), currently in version 2.3, that accommodates managed services, such as databases. This repository contains an implementaiton of a service broker for a [simplified echo service](https://github.com/dwatrous/cf-echo-service).

[Step by step example usage in CloudFoundry](http://software.danielwatrous.com/managed-services-in-cloudfoundry/)

[Step by step example usage in Stackato](http://software.danielwatrous.com/managed-services-in-stackato/)

#### Dependencies
 * Python 3.x
 * bottle (http://bottlepy.org/docs/dev/index.html)
 * requests

# Install and Run

The service broker can be run easily on any system that satisfies the dependiencies above. This repository also contains artifacts that make it easy to deploy to Stackato or HP Helion Development Platform.

## Update the echo service URL/IP
The `service_base` variable needs to be updated to point to your [running echo service](https://github.com/dwatrous/cf-echo-service) before starting the service broker.

## Windows
Clone this repository on to your Windows machine. Change into the directory where the files were cloned and use the python executable to run the script. The console session will look like the snippet below.

```
C:\Users\watrous\Documents\GitHub\cf-service-broker-python>\Python32\python.exe service-broker.py
Bottle v0.13-dev server starting up (using WSGIRefServer())...
Listening on http://0.0.0.0:8080/
Hit Ctrl-C to quit.
```

## Linux
Clone this repository on to your Linux system. Change into the directory and run the script. The session will look something like what's shown below.

```
vagrant@vagrant-ubuntu-trusty-64:~/cf-service-broker-python$ python3 service-broker.py
Bottle v0.12.7 server starting up (using WSGIRefServer())...
Listening on http://0.0.0.0:8080/
Hit Ctrl-C to quit.
```

## Deployed
The service broker script can be deployed using the stackato command line client. The snippet below shows what that looks like.

Stackato supports Python 3.3 (at least it did when I wrote this). Before pushing to stackato, update the **runtime.txt** to have "python-3.3"

```
C:\Users\watrous\Documents\GitHub\cf-service-broker-python>stackato push
Would you like to deploy from the current directory ?  [Yn]:
Using manifest file "manifest.yml"
Application Deployed URL [service-broker.stackato.danielwatrous.com]:
Application Url:   https://service-broker.stackato.danielwatrous.com
Creating Application [service-broker] as [https://api.stackato.danielwatrous.com -> Test -> somespace -> service-broker] ... OK
  Map https://service-broker.stackato.danielwatrous.com ... OK
Bind existing services to 'service-broker' ?  [yN]:
Create services to bind to 'service-broker' ?  [yN]:
Uploading Application [service-broker] ...
  Checking for bad links ...  OK
  Copying to temp space ...  OK
  Checking for available resources ...  OK
  Processing resources ... OK
  Packing application ... OK
  Uploading (4K) ...  OK
Push Status: OK
Starting Application [service-broker] ...
OK
http://service-broker.stackato.danielwatrous.com/ deployed
```

or for CloudFoundry

CloudFoundry supports Python 3.4.1 (at least it did when I wrote this). Before pushing to CloudFoundry, update the **runtime.txt** to have "python-3.4.1"

```
vagrant@vagrant-ubuntu-trusty-64:~/services/service-broker$ cf push
Using manifest file /home/vagrant/services/service-broker/manifest.yml

Creating app service-broker in org myorg / space mydept as admin...
OK

Using route service-broker.10.244.0.34.xip.io
Binding service-broker.10.244.0.34.xip.io to service-broker...
OK

Uploading service-broker...
Uploading app files from: /home/vagrant/services/service-broker
Uploading 8.2K, 4 files
Done uploading
OK

Starting app service-broker in org myorg / space mydept as admin...
-----> Downloaded app package (4.0K)
-------> Buildpack version 1.0.5
Use locally cached dependencies where possible
-----> Installing runtime (python-3.4.1)
-----> Installing dependencies with pip
       Downloading/unpacking bottle (from -r requirements.txt (line 1))
         Running setup.py (path:/tmp/pip_build_vcap/bottle/setup.py) egg_info for package bottle

       Downloading/unpacking requests (from -r requirements.txt (line 2))
       Installing collected packages: bottle, requests
         Running setup.py install for bottle
           changing mode of build/scripts-3.4/bottle.py from 644 to 755

           changing mode of /app/.heroku/python/bin/bottle.py to 755
       Successfully installed bottle requests
       Cleaning up...

-----> Uploading droplet (34M)

1 of 1 instances running

App started


OK
Showing health and status for app service-broker in org myorg / space mydept as admin...
OK

requested state: started
instances: 1/1
usage: 256M x 1 instances
urls: service-broker.10.244.0.34.xip.io
last uploaded: Fri Nov 21 20:28:19 UTC 2014

     state     since                    cpu    memory          disk
#0   running   2014-11-21 08:29:16 PM   0.0%   55.1M of 256M   0 of 1G
```

# Usage

## Catalog
The catalog returns a JSON document describing the services that are managed through this service broker implementation.

#### Request
```
GET http://localhost:8080/v2/catalog
X-Broker-Api-Version: 2.3
Authorization: Basic dXNlcjpwYXNz
```
#### Response

```
{
  "services": [
    {
      "description": "Echo back the value received",
      "dashboard_client": {
        "secret": "secret-1",
        "redirect_uri": "http://16.85.146.167:8090/echo/dashboard",
        "id": "client-id-1"
      },
      "name": "Echo Service",
      "bindable": true,
      "id": "echo_service",
      "plans": [
        {
          "description": "A large dedicated service with a big storage quota, lots of RAM, and many connections",
          "id": "big_0001",
          "free": false,
          "name": "large"
        }
      ]
    },
    {
      "description": "Invert the value received",
      "dashboard_client": null,
      "name": "Invert Service",
      "bindable": true,
      "id": "invert_service",
      "plans": [
        {
          "description": "A small shared service with a small storage quota and few connections",
          "id": "small_0001",
          "name": "small"
        }
      ]
    }
  ]
}
```

## Provision
The following PUT provisions a new resource with the echo service with the identifier `mynewinstance`. The HTTP Basic Auth header `Authorization` is required. This call expects a JSON document with details from the catalog and the organization and space.

#### Request
```
PUT http://localhost:8080/v2/service_instances/mynewinstance
Authorization: Basic dXNlcjpwYXNz

{
  "service_id":        "echo_service",
  "plan_id":           "small_0001",
  "organization_guid": "HP",
  "space_guid":        "IT"
}
```
#### Response
The response is a JSON document containing a link to the dashboard for the newly provisioned instance.

```
{"dashboard_url": "http://16.98.113.38:8090/echo/dashboard/mynewinstance"}
```

## Bind
The following PUT binds the app with identifier `myappid` to the provisioned instance `mynewinstance`. The HTTP Basic Auth header `Authorization` is required. This call expects a JSON document with details to associate a specific app, `otherappid`, with the service specific service that is being bound, `echo_service` in this case.

#### Request
```
PUT http://localhost:8080/v2/service_instances/mynewinstance/service_bindings/myappid
Authorization: Basic dXNlcjpwYXNz

{
  "service_id":        "echo_service",
  "plan_id":           "small_0001",
  "app_guid":          "otherappid"
}
```

#### Response
The response provides credentials that can be used by the app to use the service. In the case of the echo service, there is only a `uri`. These credentials will be injected into each app instance as environment variables.
```
{
  "credentials": {
    "uri": "http://16.98.113.38:8090/echo/mynewinstance/myappid"
  }
}
```

## Unbind
The following DELETE unbinds the app with identifier `myappid` from the instance `mynewinstance`. The HTTP Basic Auth header `Authorization` is required.

#### Request
```
DELETE http://localhost:8080/v2/service_instances/mynewinstance/service_bindings/myappid
Authorization: Basic dXNlcjpwYXNz
```

#### Response
A 200 response with an empty JSON document indicates success. The content-type of response is set to JSON to accommodate future enhancements, but it is currently always empty.
```
{}
```

## Deprovision
The following DELETE deprovisions an existing instance of the echo service with the identifier `mynewinstance`. The HTTP Basic Auth header `Authorization` is required.

#### Request
```
DELETE http://localhost:8080/v2/service_instances/mynewinstance
Authorization: Basic dXNlcjpwYXNz
```
#### Response
A 200 response with an empty JSON document indicates success. The content-type of response is set to JSON to accommodate future enhancements, but it is currently always empty.
```
{}
```
