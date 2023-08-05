import argparse
import json
import socket
import requests
from simpletr64.devicetr64 import DeviceTR64
from simpletr64.discover import Discover, DiscoveryResponse

#######################################################################################################################

parser = argparse.ArgumentParser(
    description="Script to discover all UPnP hosts in the network and to dump their basic information's.")
parser.add_argument("-t", "--timeout", type=str, help="timeout for network actions in seconds", default=1)
parser.add_argument("-u", "--user", type=str, help="username for authentication", default="")
parser.add_argument("-p", "--password", type=str, help="password for authentication", default="")
parser.add_argument("--http", type=str, help="proxy URL for http requests (http://proxyhost)", default="")
parser.add_argument("--https", type=str, help="proxy URL for https requests (https://proxyhost)", default="")

parser.parse_args()
args = parser.parse_args()

use_timeout = args.timeout
use_user = args.user
use_pw = args.password
use_httpProxy = args.http
use_httpsProxy = args.https

#######################################################################################################################

# setup proxies for discovery call
proxies = {}
if use_httpsProxy:
    proxies = {"https": use_httpsProxy}

if use_httpProxy:
    proxies = {"http": use_httpProxy}

print("Start discovery.")

# start a broad dicovery
results = Discover.discover()

hostResults = {}

for result in results:
    if result.locationHost not in hostResults.keys():
        hostResults[result.locationHost] = []

    # remember all results for a dedicated host, add rating for later sorting
    hostResults[result.locationHost].append({"sortKey": Discover.rateServiceTypeInResult(result), "result": result})

output = {}

print("Amount of hosts found: " + str(len(hostResults.keys())))
print("Processing: ")

# iterate through all found hosts
for host in hostResults.keys():
    sortedResults = sorted(hostResults[host], key=lambda sortit: sortit["sortKey"], reverse=True)

    output[host] = {}
    output[host]["services"] = {}

    # noinspection PyBroadException
    try:
        output[host]["hostname"] = socket.gethostbyaddr(host)[0]
        print("Host: " + output[host]["hostname"])
    except:
        print("Host: " + host)

    try:
        # get TR64 multicast result for the given host to get XML definition url
        result = Discover.discoverParticularHost(host, service=sortedResults[0]["result"].service,
                                                 retries=1, proxies=proxies, timeout=use_timeout)
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError) as e:
        # could not download the gile
        print("Host " + host + " failed: " + str(e))
        result = None

    if result is not None:
        hostResults[host].append({"sortKey": Discover.rateServiceTypeInResult(result), "result": result})

    # resort making sure we start with the important one first
    sortedResults = sorted(hostResults[host], key=lambda sortit: sortit["sortKey"], reverse=True)

    # load all xml file definitions for this host
    loadedXMLFile = []
    for sResult in sortedResults:
        if sResult["result"].location not in loadedXMLFile:
            loadedXMLFile.append(sResult["result"].location)

            # get instance of device
            box = DeviceTR64(sResult["result"].locationHost, sResult["result"].locationPort,
                             sResult["result"].locationProtocol)
            box.username = use_user
            box.password = use_pw
            box.httpProxy = use_httpProxy
            box.httpsProxy = use_httpsProxy

            try:
                # load the device definitions from the location which was in the result
                box.loadDeviceDefinitions(sResult["result"].location, timeout=use_timeout)
            except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError) as e:
                # it failed so we will have less service types later
                pass

            # add the device informations if it was in there already
            if "informations" not in output[host].keys():
                output[host]["informations"] = box.deviceInformations

            # build the full URL for convenient reasons
            url = sResult["result"].locationProtocol + "://" + sResult["result"].locationHost + \
                          ":" + str(sResult["result"].locationPort)

            # go through the services which we found in addition and add them as usual results
            for service in box.deviceServiceDefinitions.keys():
                result = DiscoveryResponse.create(url + box.deviceServiceDefinitions[service]["scpdURL"],
                                                  service=service)
                hostResults[host].append({"sortKey": Discover.rateServiceTypeInResult(result), "result": result})

    # resort as we might have added services
    sortedResults = sorted(hostResults[host], key=lambda sortit: sortit["sortKey"], reverse=True)

    # build the results together
    for sResult in sortedResults:
        if sResult["result"].service not in output[host]["services"].keys():
            output[host]["services"][sResult["result"].service] = []

        if sResult["result"].location not in output[host]["services"][sResult["result"].service]:
            output[host]["services"][sResult["result"].service].append(sResult["result"].location)

print("Results:")
# print it out in a formated way
print(json.dumps(output, indent=4, sort_keys=True, separators=(',', ': ')))
