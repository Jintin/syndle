#!/usr/bin/env python

from unittest import TestCase
import os
import shutil
import filecmp
import syndle
import syndle.gradle


class TestSyndle(TestCase):

    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

    def testParseSetting(self):
        list = syndle.gradle.list(
            self.CURRENT_PATH + "/test/settings.gradle")
        self.assertEqual(list, ["app", "lib"])

    def testParseGradle(self):
        obj = syndle.gradle.parse(
            self.CURRENT_PATH + "/test/root.gradle")

        list = ["https://www.jitpack.io", "google"]
        map = obj["buildscript"]["repositories"]
        for key in map:
            self.assertIn(key, list)

        list = ["https://www.jitpack.io", "google", "jcenter"]
        map = obj["allprojects"]["repositories"]
        for key in map:
            self.assertIn(key, list)
