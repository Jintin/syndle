import os
from unittest import TestCase

import syndle
import syndle.gradle


class TestSyndle(TestCase):
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

    def testParseSetting(self):
        projects = syndle.gradle.list(os.path.join(self.CURRENT_PATH, "test", "settings.gradle"))
        self.assertEqual(len(projects), 2)
        self.assertEqual([x["name"] for x in projects], ["app", "lib"])

    def testParseSetting2(self):
        projects = syndle.gradle.list(os.path.join(self.CURRENT_PATH, "test", "settings2.gradle"))
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["name"], "myAwesomeApp")
        self.assertFalse(projects[0]["is_subprojects"])

    def testParseSetting3(self):
        properties = syndle.load_gradle_property(os.path.join(self.CURRENT_PATH, "test",  "gradle.properties"))
        projects = syndle.gradle.list(os.path.join(self.CURRENT_PATH, "test", "settings3.gradle"), properties)
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["name"], "myAwesomeApp")
        self.assertFalse(projects[0]["is_subprojects"])

    def testParseGradle(self):
        properties = syndle.load_gradle_property(os.path.join(self.CURRENT_PATH, "test",  "gradle.properties"))
        obj = syndle.gradle.parse(self.CURRENT_PATH + "/test/root.gradle", properties)

        projects = ["https://www.jitpack.io", "google", "https://www.jitpack.io", "google", "jcenter"]
        for key in obj["buildscript"]["repositories"]:
            self.assertIn(key, projects[0:2])

        for key in obj["allprojects"]["repositories"]:
            self.assertIn(key, projects[2:])
