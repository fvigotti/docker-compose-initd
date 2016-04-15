import unittest
#from pydservice import *
import pydservice.pydservice as pydservice

import os
class IntegrationTest(unittest.TestCase):

    def getTestResourcePath(self, composeFilename):
        #print os.path.dirname(os.path.abspath(__file__)) + "/"+  composeFilename;
        return os.path.dirname(os.path.abspath(__file__)) + "/"+  composeFilename

    def testGetContainerNames(self):
        composeYmlFile = pydservice.DockerComposeYmlFile(self.getTestResourcePath("composeFiles/TwoContainers.yml"))

        self.assertTrue(
            "db" in composeYmlFile.getContainerNames())
        self.assertTrue(
            "web" in composeYmlFile.getContainerNames())
        self.assertFalse(
            "wab" in composeYmlFile.getContainerNames())
        self.assertEquals(2 , len(composeYmlFile.getContainerNames()))

    class ExternalCommandsExecutorStub():
        def __init__(self, outputStubbed):
            self.outputStubbed = outputStubbed

        def run(self,*args):
            return self.outputStubbed

    class InputAwareExternalCommandsExecutorStub():
        def __init__(self, expectedExecutionInput, fakeExecutionOutput):
            self.expectedExecutionInput = expectedExecutionInput
            self.fakeExecutionOutput = fakeExecutionOutput

        def run(self,*args):
            return self.outputStubbed


    def testGetContainersIdsWhenContainersDoesntExists(self):
        # setup
        ymlFile = self.getTestResourcePath("composeFiles/TwoContainers.yml")
        commandOutput = "\n"
        stubcommandExecutor = IntegrationTest.ExternalCommandsExecutorStub(commandOutput)

        #test
        dockerCompose = pydservice.DockerCompose(ymlFile, stubcommandExecutor)
        self.assertEquals(len(dockerCompose.getContainersIds()), 0 )


    def testGetContainersIds(self):
        # setup
        ymlFile = self.getTestResourcePath("composeFiles/TwoContainers.yml")
        commandOutput = ("17a3b654883cb4666b0f039f224c5f105b55ea929781d04518eb46a94883a841\n"
                         "6b86642d4eb0e17ea60cdbcf8df8c32527ba9ad5276273658bfda13bcdeb581f\n")
        stubcommandExecutor = IntegrationTest.ExternalCommandsExecutorStub(commandOutput)

        #test
        dockerCompose = pydservice.DockerCompose(ymlFile, stubcommandExecutor)
        self.assertEquals(len(dockerCompose.getContainersIds()), 2 )

    def testInspectorReturnNoneWhenContainerIdIsNotFound(self):
        commandOutput = "[]\n"
        containerId = "notExistentContainer"
        stubcommandExecutor = IntegrationTest.ExternalCommandsExecutorStub(commandOutput)
        inspector = pydservice.DockerInspector(stubcommandExecutor)
        inspection = inspector.inspect(containerId)
        self.assertIsNone(inspection)

    def testInspectorReturnContainerValidRunningInspectionObjectWhenIsfound(self):

        with open(self.getTestResourcePath("resources/DockerInspect_validResults.json"), 'r') as stream:
            fileContent = stream.read()

        self.assertGreater(len(fileContent) , 0)

        containerId = "stubbedExistingContainer"

        stubcommandExecutor = IntegrationTest.ExternalCommandsExecutorStub(fileContent)
        inspector = pydservice.DockerInspector(stubcommandExecutor)
        inspection = inspector.inspect(containerId)
        self.assertIsNotNone(inspection)
        self.assertTrue(inspection.isRunning())

    def testInspectionOfNotRunningContainerReturn_IsRunning_False(self):
        with open(self.getTestResourcePath("resources/DockerInspect_StoppedContainerResults.json"), 'r') as stream:
            fileContent = stream.read()

        containerId = "stubbedExistingContainer"
        stubcommandExecutor = IntegrationTest.ExternalCommandsExecutorStub(fileContent)
        inspector = pydservice.DockerInspector(stubcommandExecutor)
        inspection = inspector.inspect(containerId)
        self.assertFalse(inspection.isRunning())

    

    def testFoo(self):
        ymlPath = self.getTestResourcePath("composeFiles/TwoContainers.yml")

        expectedExecutionInput = [
            ['docker-compose', '-f', ymlPath, 'ps', '-q'],
            ['docker', 'inspect', 'id1'],
            ['docker', 'inspect', 'id2'],
        ]
        fakeExecutionOutput = [
            'id1\nid2\n',
            '[{"State": {"Running": true}}]',
            '[{"State": {"Running": true}}]',
        ]

        stubcommandExecutor = IntegrationTest.InputAwareExternalCommandsExecutorStub(expectedExecutionInput, fakeExecutionOutput)
        outputStream = IntegrationTest.StreamStub()

        contextFactory = IntegrationTest.ContextFactoryStub(stubcommandExecutor, outputStream)

        command = pydservice.StatusCommand(ymlPath, contextFactory)
        exitCode = command.execute()

        self.assertEquals(0, exitCode)
        self.assertEquals('Running', outputStream.content)

    
    class StreamStub(object):
        def __init__(self):
            self.content = ""

        def write(self, message):
            self.content += message

    class ContextFactoryStub(object):
        def __init__(self, executor, output):
            self.executor = executor
            self.output = output

        def buildOutputStream(self):
            return self.output


if __name__ == '__main__':
    unittest.main()
