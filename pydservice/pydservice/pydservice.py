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

class ContextFactory(object):
    def setExternalCommandsExecutor(self, executor):
        self.executor = executor
    def setOutputStream(self, output):
        self.output = output

    def buildOutputStream(self):
        return self.output

class StatusCommand(object):
    def __init__(self, ymlPath, contextFactory):
        self.outputStream = contextFactory.buildOutputStream()

    def execute(self):
        self.outputStream.write('Running') 
        return 0

class DockerComposeYmlFile(object):

    def __init__(self,composeYmlFile):
        with open(composeYmlFile, 'r') as stream:
            self.YMLContent  = yaml.load(stream)

    def getContainerNames(self):
        return self.YMLContent['services'].keys()

class DockerCompose(object):
    def __init__(self,composeYmlFile,externalCommandsExecutor):
        self.externalCommandsExecutor = externalCommandsExecutor
        self.composeYmlFile = composeYmlFile

    def getContainersIds(self):
        return filter( lambda x : x!= "", self.externalCommandsExecutor.run('docker-compose', "-f",self.composeYmlFile,"ps","-q").split("\n") )

class ExternalCommandsExecutor(object):
        def run(self,*args):
            return subprocess.check_output(args)


class ContainerInspection(object):

    def __init__(self,inspectionObject):
        self.inspectionObject = inspectionObject

    def isRunning(self):
        return self.inspectionObject['State']['Running']


class DockerInspector(object):
    def __init__(self,externalCommandsExecutor):
        self.externalCommandsExecutor = externalCommandsExecutor

    def inspect(self,containerId):
        inspectionResults = self.externalCommandsExecutor.run("docker","inspect",containerId)
        jsonResults = json.loads(inspectionResults)
        if len(jsonResults) == 0:
            return None

        return ContainerInspection(jsonResults[0])




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

#print "stopping containers : " , stopContainers(composeYmlFile);

# "MUST_ALWAYS_RUN=false"
