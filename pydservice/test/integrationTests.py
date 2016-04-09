import unittest
#from pydservice import *
import pydservice.pydservice as pydservice

import os
class TestStringMethods(unittest.TestCase):

  def getFullComposePath(self,composeFilename):
      print os.path.dirname(os.path.abspath(__file__)) + "/"+  composeFilename;
      return os.path.dirname(os.path.abspath(__file__)) + "/"+  composeFilename

  def test_TwoContainersOneVolume(self):
      #print type(pydservice.startContainers)
      pydservice.startContainers(self.getFullComposePath("composeFiles/ThreeContainersOneVolume.yml"))
      pydservice.stopContainers(self.getFullComposePath("composeFiles/ThreeContainersOneVolume.yml"))

      #self.assertEqual('foo'.upper(), 'FOO')

  def test_isupper(self):
      self.assertTrue('FOO'.isupper())
      self.assertFalse('Foo'.isupper())

  def test_split(self):
      s = 'hello world'
      self.assertEqual(s.split(), ['hello', 'world'])
      # check that s.split fails when the separator is not a string
      with self.assertRaises(TypeError):
          s.split(2)

if __name__ == '__main__':
    unittest.main()
