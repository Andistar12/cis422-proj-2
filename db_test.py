"""
Unit tests for database interaction

To run the tests on this file do the following:
    Basic test:
        $ python3 db_test.py
    Verbose test to see each test function's success or failure:
        $ python3 -m unittest -v db_test.py
    Test with performance profiling:
        $ python3 -m cProfile -s cumtime tsp_tests.py
"""

import pymongo
import os
import sys
import json
import logging
import unittest

from db import AppDB

class DBTests(unittest.TestCase):
    """
    Unit test driver for db.py
    """

    def setUp(self):
        """
        Sets up the MongoClient
        """

        # Determine the appropriate config file location
        cfgloc = "./config.json"
        # Read files from config
        try:
            with open(cfgloc) as cfgfile:
                config = json.load(cfgfile)
        except:
            logging.getLogger("server").error("Error occurred opening config file", exc_info=True)
            config = {}

        # Fetch config parameters
        try:
            db_link = config.get("db_link", "")
            client = pymongo.MongoClient(db_link)
            self.db = AppDB(client)
        except:
            logging.getLogger("server").error("Error occurred creating mongo client", exc_info=True)
            self.db = None

    def test_example(self):
        pass
        self.assertEqual(True, True)

    def test_add_user(self):
        self.db.add_user("Andistar12", "super secret password")
        user = self.db.fetch_user("Andistar12")
        self.assertIsNotNone(user)
        self.assertIn("password", user)
        self.assertEqual(user["password"], "super secret password")

if __name__ == "__main__":
    unittest.main(module="db_test")