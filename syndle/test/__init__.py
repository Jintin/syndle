import os
from unittest import TestCase

import syndle
import syndle.gradle


class TestSyndle(TestCase):
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

    def testParseSetting(self):
        projects = syndle.gradle.list(os.path.join(self.CURRENT_PATH, "test", "settings.gradle"))
        self.assertEqual(projects, ["app", "lib"])

    def testParseSetting2(self):
        projects = syndle.gradle.list(os.path.join(self.CURRENT_PATH, "test", "settings2.gradle"))
        self.assertEqual(projects, ["myAwesomeApp"])

    def testParseSetting3(self):
        projects = syndle.gradle.list(os.path.join(self.CURRENT_PATH, "test", "settings3.gradle"))
        self.assertEqual(projects, ["myAwesomeApp"])

    def testParseGradle(self):
        obj = syndle.gradle.parse(self.CURRENT_PATH + "/test/root.gradle")

        projects = ["https://www.jitpack.io", "google", "https://www.jitpack.io", "google", "jcenter"]
        for key in obj["buildscript"]["repositories"]:
            self.assertIn(key, projects[0:2])

        for key in obj["allprojects"]["repositories"]:
            self.assertIn(key, projects[2:])
