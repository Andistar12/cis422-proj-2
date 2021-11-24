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
            self.users=client.p2_db.users
            self.admins=client.p2_db.admins
            self.boards=client.p2_db.boards
            self.comments=client.p2_db.comments
        except:
            logging.getLogger("server").error("Error occurred creating mongo client", exc_info=True)
            self.db = None


    def test_userandadmin(self):
        username="tchen4"
        self.users.delete_many({"username":username})
        self.users.delete_many({"username": username})
        self.db.add_user(username, "2121")
        user = self.db.fetch_user(None,username)
        self.assertNotEqual({},user)
        check=self.users.find_one({"username":username})
        self.assertNotEqual(None,check)
        self.db.remove_user(None,username)
        check = self.users.find_one({"username": username})
        self.assertEqual(None,check)

        username="tchen4"
        self.db.add_user(username,'2121')
        self.db.add_admin(None,username)
        admin=self.db.fetch_admins()
        self.assertNotEqual([],admin)
        check = self.admins.find_one({"username": username})
        self.assertNotEqual(None, check)
        self.db.remove_admin(None,username)
        check = self.admins.find_one({"username": username})
        self.assertEqual(None, check)
        self.db.add_admin(None, username)

    def test_boardandpost(self):
        username="tchen4"
        boardname="board4"
        self.boards.delete_many({"board_name": boardname})
        userid=self.users.find_one({"username":username})["_id"]
        boardid=self.db.create_board(None,username,boardname,"1",10)
        board=self.db.fetch_board(boardid)
        self.assertNotEqual({},board)
        boards=self.db.fetch_boards(boardname,0,False)
        self.assertNotEqual([],boards)
        self.db.subscribe_board(None,username,boardid)
        board = self.db.fetch_board(boardid)
        self.assertIn(userid,board["board_members"])
        self.db.unsubscribe_board(None, username, boardid)
        board = self.db.fetch_board(boardid)
        self.assertNotIn(userid, board["board_members"])
        self.db.delete_board(None,username,boardid)
        board=self.db.fetch_board(boardid)
        self.assertEqual({},board)
        boardid = self.db.create_board(None, username, boardname, "1", 10)

        self.db.subscribe_board(None, username, boardid)
        postid=self.db.create_post(None,username,boardid,"1","1")
        post=self.db.fetch_post(boardid,postid)
        self.assertNotEqual({},post)
        self.db.upvote_post(None,username,boardid,postid)
        post = self.db.fetch_post(boardid, postid)
        self.assertIn(userid,post["post_upvoters"])
        self.db.unupvote_post(None, username, boardid, postid)
        post = self.db.fetch_post(boardid, postid)
        self.assertNotIn(userid, post["post_upvoters"])
        self.db.notify_post(boardid,postid)
        post = self.db.fetch_post(boardid, postid)
        self.assertEqual(1,post["post_notified"])
        self.db.delete_post(None,username,boardid,postid)
        post=self.db.fetch_post(boardid,postid)
        self.assertEqual({},post)


if __name__ == "__main__":
    unittest.main(module="db_test")