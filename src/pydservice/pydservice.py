#!/usr/bin/env python

import yaml
import subprocess
import json
from subprocess import call


"""
conventions :
    at least 1 service must exist in the docker compose file
    containers that can be down (ie: volumes) should have env variable : "MUST_ALWAYS_RUN=false"
"""

composeYmlFile = "../../test/resources/composesample/twoUpOneVolume.yml"
dockerComposeCMD =  "/usr/local/bin/docker-compose"
dockerCMD =  "/usr/bin/docker"

def parseYml(composeYmlFile):
    with open(composeYmlFile, 'r') as stream:
        try:
            return yaml.load(stream);
        except yaml.YAMLError as exc:
            print(exc)


def checkErrorInput(f):
    def runner(input):
        if input == Error:
            return input
        return f(input)
    return runner

#@checkErrorInput
def getServicesId(composeYmlFile):
    """
    extract an array with ids of dockerized services created
    """
    return subprocess.check_output([dockerComposeCMD, "-f",composeYmlFile,"ps","-q"]).split("\n")[:-1]

#@checkErrorInput
def inspectContainers(containersIds):
    """
    return an array of json object containing status
    """

    return subprocess.check_output( [dockerCMD, "inspect"] + containersIds)

def isContainerOk(containerObj):
    containerMustBeUp = True;

    for envProperty in containerObj['Config']["Env"]:
        containerMustBeUp = containerMustBeUp and (
                                        envProperty.lower().find("MUST_ALWAYS_RUN=false".lower()) == -1 )

    isContainerUp = containerObj['State']["Running"]
    #if containerMustBeUp and
    #print "containerMustBeUp ?  = " , containerMustBeUp , " isup ? " , isContainerUp
    if containerMustBeUp and not isContainerUp:
        print "error! container ", containerObj['Name'] ," is in wrong state"
        return False
    return True

def parseContainerProperties(containersPropertiesStr):
    return json.loads(containersPropertiesStr)

def checkStatus(containersPropertiesObj):
    """
    return true if status is ok ( all containers are in consistent state)
    return false if some container is in wrong state
    """
    #filter(lambda x: x > 5 and x < 50, squares)
    return reduce ( lambda x,y : x and isContainerOk(y)   , containersPropertiesObj , True)
    #for containerProperties in containersPropertiesObj:
        #checkContainerStatus(containerProperties)


def stopContainers(composeYmlFile):
    return subprocess.check_output([dockerComposeCMD, "-f",composeYmlFile,"stop"])

def deleteContainers(composeYmlFile):
    return subprocess.check_output([dockerComposeCMD, "-f",composeYmlFile,"rm","-f"])

def startContainers(composeYmlFile):
    return subprocess.check_output([dockerComposeCMD, "-f",composeYmlFile,"up","-d"])

def smartStart(composeYmlFile):
    if not checkContainersStatus():
        startContainers(composeYmlFile)
    if not checkContainersStatus():
        stopContainers()
        startContainers(composeYmlFile)
    if not checkContainersStatus():
        deleteContainers()
        startContainers(composeYmlFile)


def checkContainersStatus():
    #print "YAML : ", parseYml(composeYmlFile)
    servicesIdList = getServicesId(composeYmlFile)

    if(len(servicesIdList) < 1):
        print "no services defined"
        return False
    else:
        print "services id : " , servicesIdList
        #print "inspection : ", inspectContainers(getServicesId(composeYmlFile))
        containerStatus = checkStatus(
                parseContainerProperties(
                    inspectContainers(
                        servicesIdList)))
        print "service status : ",containerStatus ;
        return containerStatus;

print "stopping containers : " , stopContainers(composeYmlFile);

# "MUST_ALWAYS_RUN=false"
