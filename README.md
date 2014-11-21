CloudFoundry Service Broker v2 implementation in Python
========================

CloudFoundry (and Stackato and HP Helion Development Platform) provide a Service Broker API (http://docs.cloudfoundry.org/services/api.html), currently in version 2.3, that accommodates managed services, such as databases. This repository contains an implementaiton of a service broker for a [simplified echo service](https://github.com/dwatrous/cf-echo-service).

#### Dependencies
 * Python 3.x
 * bottle (http://bottlepy.org/docs/dev/index.html)
 * requests

# Usage

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
Using the stackato or helion cli, the script can be deployed. The snippet below shows what that looks like.

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
