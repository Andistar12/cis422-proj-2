"""
Handles all database transactions.

The database has a number of MongoDB collections:
 - users: contains information about users
 - admins: contains information about system administrators
 - boards: contains information about boards
 - posts: contains posts and comments

In the users collection, each user entry has the following form:
{   "_id": id of user
    "username": username of the person. This is the unique identifier for the user
    "password": hashed password of the user
    "subscriptions": list of board IDs
    "admin": whether the user is an administrator
    "last_active_date": last active date
    "boards_owned": the board id of the board that the user made
    "posts_owned": the posts id of the post that the user posted
    "comments_owned": the comment id of the comments that the user made
}

In the admins collection, each admin entry has the following form:
{
    "_id": id of admins
    "username": username of the admin. This is the unique identifier for the administrator
    "userid": userid of the admins
}

In the boards collection, each board entry has the following form:
{
    "_id": unique ID of the board
    "board_name": name of the board
    "board_description": description of the board
    "board_date": creation date of the board
    "board_member_count": number of members on the board
    "board_members": list of members id in the board
    "board_vote_threshold": the percentage of community required for vote
    "board_owner": owner id of the board
    "last_active_date": last active date
    "posts_id": array of id of the posts


}

In a particular board's collection, each entry is a post which has the following form:
{
    "_id": unique ID of the board
    "board_id": the id of the board it belongs to
    "post_subject": subject of the post
    "post_description": description of the post
    "post_owner": owner id of the post
    "post_date": creation date of the post
    "post_upvotes": number of upvotes on the post
    "post_upvoters": list of user IDs who voted on the post
    "post_notified": whether the post notification has already been triggered
    "post_comments": list of comments dictionaries
    "last_active_date": last active date

}

Comments has the following form:
{
    "_id": unique ID of the comment
    "comment_owner": owner id of the comment
    "comment_message": message content of the comment
    "comment_date": creation date of the comment
    "comment_upvotes": number of upvotes on the comment
    "comment_upvoters": list of user IDs who voted on the comment
}

"""

import pymongo
import datetime
import re
from pymongo import MongoClient
from bson.objectid import ObjectId



class AppDB:
    """
    The manager for all database transactions
    """

    def __init__(self):
        """
        Initiates the AppDB manager

        Parameters:
         - client: the MongoDB client
        """
        self.client = MongoClient("mongodb+srv://tchen3:2964@cluster0.6se93.mongodb.net/p2_app_db?retryWrites=true&w=majority")
        self.db=self.client.p2_db




    def fetch_user(self, userid: ObjectId, user_name: str ):
        """
        Returns information about a user if exists

        Parameters:
         - userid: the id of the user
         - username: the username of the user
         NOTE: use only userid or username, pass "None" to unused parameters!
        Returns:
         - A dictionary container the user information
        Error: return empty dictionary
        """
        user = self.db.users
        if userid==None:
            filter ={"username":user_name}
        else:
            filter={"_id":userid}
        val=user.find_one(filter)
        if val==None:
            return {}
        else:
            return val


    def add_user(self, user_name: str, password: str):
        """
        Adds a user to the database

        Parameters:
         - username: the username to use
         - password: the hashed password to use
        Return: An object of ID (created by MongoDB) of user added
        Error: return None
        """
        user=self.db.users

        if(user.find_one({"username":user_name})!=None):
            return None
        else:
            user.insert_one({"username":user_name,
                         "password":password,
                         "subscriptions":[],
                         "admin":0,
                         "last_active_date":None,
                         "boards_owned":[],
                         "posts_owned":[],
                         "comments_owned":[]})
            return user.find_one({"username":user_name})["_id"]

    def remove_user(self, userid: ObjectId, user_name: str):
        """
        Removes a user from the database if exists

        Parameters:
         - userid: the id of the user
         - username: the username of the user to remove
         NOTE: use only userid or username, pass "None" to unused parameters!
        Return: An object of ID (created by MongoDB) of user removed
        Error: return None
        """
        user=self.db.users
        board=self.db.boards
        if userid==None:
            filter={"username":user_name}
        else:
            filter={"_id":userid}
        val=user.find_one(filter)
        if val != None:
            user.delete_one(filter)
            subs=val["subscriptions"]
            for id in subs:
                board.update_one({"_id":id},{"$pull":{"board_members":val["_id"]}})
                board.update_one({"_id": id}, {"$inc": {"board_member_count": 1}})

            return val["_id"]
        else:
            return None


    def add_admin(self, userid: ObjectId, user_name: str):
        """
        Adds an administrator to the system. This has no effect if the user is already an administrator

        Parameters:
         - userid: the id of the user
         - username: the username of the administrator
        NOTE: use only userid or username, pass "None" to unused parameters!
        Return: An object of ID (created by MongoDB) of admin added
        Error: return None
        """
        user = self.db.users
        admin=self.db.admins
        if userid==None:
            filter={"username": user_name}
        else:
            filter={"_id":userid}
        val=user.find_one(filter)
        if val!=None:
            if val["admin"]!=1:
                user.update_one({"username": user_name},{"$set":{"admin":1}})
                admin.insert_one({"username":user_name,
                                  "userid":val["_id"]})
                return admin.find_one({"username":user_name})["_id"]
        else:
            return None

    def remove_admin(self, userid: ObjectId, user_name: str):
        """
        Removes an administrator from the system.

        Parameters:
         - userid: the id of the user
         - username: the username of the administrator to remove
        NOTE: use only userid or username, pass "None" to unused parameters!
        Return: An object of ID (created by MongoDB) of admin removed
        Error: return None
        """
        user = self.db.users
        admin = self.db.admins
        if userid==None:
            filter={"username":user_name}
        else:
            filter ={"_id":userid}
        val=admin.find_one(filter)
        if val != None:
            admin.delete_one(filter)
            user.update_one(filter, {"$set": {"admin": 0}})
            return val["_id"]
        else:
            return None



    def fetch_admins(self):
        """
        Fetches all admins of the system.

        Parameters:
         - None
         Returns:
         - An array of dictionaries, each dictionary containing information about an administrator
         Error: return empty array
        """
        admin=self.db.admins
        return list(admin.find())


    def fetch_boards(self, keyword: str, offset: int):
        """
        Returns up to 50 boards. The ordering of the boards may be catered to the user
        - Posts are not included
        Parameters:
         - keyword: a search string to filter results by
         - offset: offset into board results. For example, an offset of 1 will
                    return boards 50 through 99
        Returns:
         - An array of dictionaries, each dictionary containing information about a board
        Error: return empty array
        """
        board=self.db.boards
        regx=re.compile(keyword,re.IGNORECASE)
        array=list(board.find({"$or":[{"board_name":regx},
                        {"board_description":regx}]},
                        ))

        return array[offset*50:(offset+1)*50]

    def fetch_board(self, boardid: ObjectId, boardname: str):
        """
        Fetches information about a single board.

        NOTE: DOES NOT include posts, call "fetch_posts()" to get sorted posts!

        Parameters:
         - boardid: the unique board ID
         - boardname : board name
        NOTE: use only boardid or boardname, pass "None" to unused parameters!
        Return: dictionary containing board information
        Error: return empty dictionary
        """
        board=self.db.boards
        if boardid == None:
            filter = {"board_name": boardname}
        else:
            filter = {"_id": boardid}
        val = board.find(filter)
        if val != None:
            return board.find_one(filter)
        else:
            return {}

    def create_board(self, ownerid: ObjectId, owner: str, boardname: str, desc: str, vote_threshold: int):
        """
        Creates a new board and assigns it a unique ID.

        The creation date of the board is set to now.

        Parameters:
         - ownerid: id of the owner
         - owner : name of the owner
         NOTE: use only ownerid or owner, pass "None" to unused parameters!
         - boardname: the name of the board
         - desc: the description of the board
         - vote_threshold: the vote threshold for the board
        Returns:
         - The unique ID Object of the new board, or None if an error occurs
        Error: return None
        """
        board=self.db.boards
        user=self.db.users
        if(board.find_one({"board_name":boardname})!=None):
            return None
        else:
            if ownerid==None:
                filter={"username":owner}
            else:
                filter={"_id":ownerid}
            theowner=user.find_one(filter)
            if theowner!=None:
                board.insert_one({"board_name":boardname,
                                "board_description":desc,
                                "board_date":datetime.datetime.now(),
                                "board_member_count":0,
                                "board_members":[],
                                "board_vote_threshold":vote_threshold,
                                "board_owner":theowner["_id"],
                                "last_active_date":None,
                                "posts_id":[]})
                return board.find_one({"board_name":boardname})["_id"]

    def delete_board(self, ownerid: ObjectId, owner: str, boardid: ObjectId, boardname: str):
        """
        Deletes a board from the database.

        All users are automatically unsubscribed from the deleted board.

        Parameters:
         - ownerid : id of the owner
         - owner : name of the owner
         NOTE: use only ownerid or owner, pass "None" to unused parameters!
         - boardid: the board ID to delete
         - boardname : the board name to delete
         NOTE: use only boardid or boardname, pass "None" to unused parameters!
        Return: the id of board deleted
        Error: return None
        """
        board = self.db.boards
        user=self.db.users
        admin=self.db.admins
        post=self.db.posts
        if boardid==None:
            filter={"board_name":boardname}
        else:
            filter={"_id":boardid}
        val=board.find_one(filter)
        if val != None:
            if ownerid==None:
                id=user.find_one({"username":owner})["_id"]
            else:
                id=ownerid
            if (id==val["board_owner"]) or (admin.find_one({"userid":id})!=None):
                board.delete_one(filter)
                member = val["board_members"]
                posts=val["posts_id"]
                for uid in member:
                    user.update_one({"_id": uid}, {"$pull": {"subscriptions": val["_id"]}})
                for pid in posts:
                    post.delete_one({"_id":pid})
                return val["_id"]
        else:
            return None



    def purge_boards(self, days: int):
        """
        Purges all boards with no activity in recent time.

        All users are automatically unsubscribed from the deleted boards.

        This is an expensive operation.

        Parameters:
         - days: the number of days from today by which boards should be deleted.
                Posts older than "days" days from today should be deleted
        """
        pass  # TODO

    def subscribe_board(self, userid: ObjectId, user_name: str, boardid: ObjectId, boardname: str):
        """
        Subscribes a user to a board.

        Parameters:
         - userid: the id of the user
         - user_name: the user that is subscribing
         NOTE: use only userid or user_name, pass "None" to unused parameters!
         - boardid: the ID of the board the user is subscribing to
         - boardname: name of the board
         NOTE: use only boardid or boardname, pass "None" to unused parameters!
         Return: subscribed board id
         Error: return None
        """
        user=self.db.users
        board=self.db.boards
        if userid==None:
            u_filter={"username": user_name}
        else:
            u_filter={"_id":userid}
        if boardid==None:
            b_filter ={"board_name":boardname}
        else:
            b_filter={"_id": boardid}
        theuser=user.find_one(u_filter)
        theboard=board.find_one(b_filter)
        if (theuser!=None) and (theboard!=None):
            user.update_one(u_filter,{"$push":{"subscriptions":boardid}})
            board.update_one(b_filter,{"$push":{"board_members":theuser["_id"]}})
            board.update_one(b_filter, {"$inc": {"board_member_count": 1}})
            return theboard["_id"]
        else:
            return None

    def unsubscribe_board(self, userid: ObjectId, user_name: str, boardid: ObjectId, boardname: str):
        """
        Unsubscribes a user to a board.

        Parameters:
        - userid: the id of the user
        - user_name: the user that is subscribing
        - board_id: the ID of the board the user is subscribing to
        - boardname: name of the board
        NOTE: use only boardid or boardname, pass "None" to unused parameters!
        NOTE: use only userid or user_name, pass "None" to unused parameters!
        Return: the unsubscribed board id
        Error: return None
        """
        user = self.db.users
        board = self.db.boards
        if userid == None:
            u_filter = {"username": user_name}
        else:
            u_filter = {"_id": userid}
        if boardid==None:
            b_filter ={"board_name":boardname}
        else:
            b_filter={"_id": boardid}
        theuser = user.find_one(u_filter)
        theboard = board.find_one(b_filter)
        if (theuser != None) and (theboard != None):
            user.update_one(u_filter, {"$pull": {"subscriptions": boardid}})
            board.update_one(b_filter, {"$pull": {"board_members": theuser["_id"]}})
            board.update_one(b_filter, {"$inc": {"board_member_count": -1}})
            return theboard["_id"]
        else:
            return None

    def fetch_post(self, board_id: ObjectId, boardname: str,  post_id: ObjectId):
        """
        Fetches all information about a single post.

        Comments will be sorted by upvote in descreasing order.

        Parameters:
         - board_id: the ID of the board the post belongs under
         - boardname: name of the board
         - post_id: the ID of the post to fetch
        NOTE: use only boardid or boardname, pass "None" to unused parameters!

        Returns:
         -  A dictionaries of posts
        Error:return empty dictionary
        """
        board = self.db.boards
        post = self.db.posts
        if board_id == None:
            b_filter = {"board_name": boardname}

        else:
            b_filter = {"_id": board_id}

        thepost=post.find_one({"_id":post_id})
        theboard=board.find_one(b_filter)
        if (thepost!=None) and (theboard!=None):
            post.update_one({"_id":post_id}, {"$push": {"post_comments": {"$each": [], "$sort": {"comment_upvotes": -1}}}})
            return post.find_one({"_id":post_id})
        else:
            return {}

    def fetch_posts(self, board_id: ObjectId, boardname: str):
        """
        Fetches all information about posts in a board

        posts will be sorted by upvote in descreasing order.

        Parameters:
         - board_id: the ID of the board the post belongs under
         - boardname: name of the board

        NOTE: use only boardid or boardname, pass "None" to unused parameters!

        Returns:
         -  An array of dictionaries of posts
        Error:return empty array
        """
        board = self.db.boards
        post = self.db.posts
        if board_id == None:
            b_filter = {"board_name": boardname}

        else:
            b_filter = {"_id": board_id}

        theboard=board.find_one(b_filter)
        if  (theboard!=None):
            return list(post.find({"board_id": theboard["_id"]}).sort("post_upvotes",pymongo.DESCENDING))

        else:
            return []

    def create_post(self, ownerid: ObjectId, owner: str, board_id: ObjectId, boardname: str,  subject: str, description: str):
        """
        Creates a post

        The creation date of the post is set to now.

        Parameters:
         - ownerid: the user id who is creating the post
         - owner: owner of the post
         - board_id: the ID of the board the post belongs under
         - boardname: board name
         NOTE: use only ownerid or owner, pass "None" to unused parameters!
         NOTE: use only boardid or boardname, pass "None" to unused parameters!
         - subject: the subject of the post
         - description: the description of the post
        Returns:
         - The unique ID of the new post
        Error: return None
        """
        user=self.db.users
        board=self.db.boards
        post=self.db.posts
        if board_id==None:
            b_filter={"board_name":boardname}
        else:
            b_filter={"_id":board_id}
        if ownerid==None:
            o_filter={"username":owner}
        else:
            o_filter={"_id":ownerid}
        theowner=user.find_one(o_filter)
        theboard=board.find_one(b_filter)
        if (theowner!=None) and (theboard!=None):

            post.insert_one({"board_id":theboard["_id"],
                             "post_subject":subject,
                             "post_description":description,
                             "post_owner":theowner["_id"],
                             "post_date":datetime.datetime.now(),
                             "post_upvotes":0,
                             "post_upvoters":[],
                             "post_notified":0,
                             "post_comments":[],
                             "last_active_date":None})

            return post.find_one({"board_id":theboard["_id"]})["_id"]
        else:
            return None

    def delete_post(self, ownerid: ObjectId, owner: str,   post_id: ObjectId):
        """
        Deletes a post.

        Parameters:
         - ownerid: id of the owner of the post
         - owner: name of the owner

         NOTE: use only ownerid or owner, pass "None" to unused parameters!

         - post_id: the ID of the post to delete
         Return: the id of deleted post
         Error: return None
        """
        user = self.db.users
        board = self.db.boards
        admin=self.db.admins
        post=self.db.posts

        if ownerid == None:
            o_filter = {"username": owner}

        else:
            o_filter = {"_id": ownerid}
        theowner = user.find_one(o_filter)
        thepost = post.find_one({"_id":post_id})
        if (theowner["_id"] ==thepost["post_owner"] ) and (thepost != None):
                #check owner: to be implemented
                post.delete_one({"_id":post_id})
                post.update_one({"_id":thepost["board_id"]},{"$pull":{"posts_id":post_id}})
                return post_id
        else:
            return None

    def upvote_post(self, upvoterid: ObjectId, upvoter: str, post_id: ObjectId):
        """
        Upvotes a post. Rescinds the upvote if the user already upvoted it.

        Parameters:
         - upvoter id: id of the upvoter
         - upvoter: name of the upvoter

         NOTE: use only upvoterid or upvotername, pass "None" to unused parameters!
         - post_id: the ID of the post to upvote
         Return: id of post upvoted
         Error: Return None
        """
        user = self.db.users
        board = self.db.boards
        post=self.db.posts

        if upvoterid == None:
            u_filter = {"username": upvoter}
        else:
            u_filter = {"_id": upvoterid}
        thepost = post.find_one({"_id":post_id})
        theupvoter = user.find_one(u_filter)
        if (theupvoter != None) and (thepost != None):
            post.update_one({"_id":post_id}, {"$push":{"post_upvoters":theupvoter["_id"]}})
            post.update_one({"_id": post_id}, {"$inc": {"post_upvotes": 1}})
            return post_id
        else:
            return None

    def purge_posts(self, board_id: str, days: int):
        """
        Purges all posts older than a given number of days.

        This is an expensive operation.

        Parameters:
         - board_id: the ID of the board to purge
         - days: the number of days from today by which posts should be deleted.
                Posts older than "days" days from today should be deleted
        """
        pass  # TODO

    def add_comment(self, ownerid: ObjectId, owner: str,  post_id: ObjectId,  message: str):
        """
        Adds a comment to a post.

        Parameters:
         - ownerid: id of the owner
         - owner: name of the owner

         NOTE: use only ownerid or owner, pass "None" to unused parameters!
         NOTE: use only boardid or boardname, pass "None" to unused parameters!
         - post_id: the ID of the post the comment falls under
         - message: the message content of the comment
         Return: id of the comment added
         Error: return None
        """
        user = self.db.users
        board = self.db.boards
        post=self.db.posts
        if ownerid == None:
            o_filter = {"username": owner}
        else:
            o_filter = {"_id": ownerid}
        theowner = user.find_one(o_filter)
        thepost = post.find_one({"_id":post_id})
        if (theowner != None) and (thepost != None):
            comment_id=ObjectId()

            post.update_one({"_id":post_id}, {"$push": {"post_comments":
                                                                {"_id":comment_id,
                                                                "comment_owner":theowner["_id"],
                                                                "comment_message":message,
                                                                "comment_date":datetime.datetime.now(),
                                                                "comment_upvotes":0,
                                                                "comment_upvoters":[]}}}
                                                                )
            return comment_id
        else:
            return None

    def delete_comment(self, ownerid: ObjectId, owner: str,  post_id: ObjectId, comment_id: ObjectId):
        """
        Removes a comment from a post.

        Parameters:
         - ownerid: id of the owner
         - owner: name of the owner

         NOTE: use only ownerid or owner, pass "None" to unused parameters!
         NOTE: use only boardid or boardname, pass "None" to unused parameters!
         - post_id: the ID of the post the comment falls under
         - comment_id: id of the comment
         Return: id of the comment deleted
         Error: return None
        """

        user = self.db.users
        board = self.db.boards
        admin = self.db.admins
        post=self.db.admins


        if ownerid == None:
            o_filter = {"username": owner}

        else:
            o_filter = {"_id": ownerid}
        theowner = user.find_one(o_filter)
        thecomment = post.find_one({"_id":post_id})
        if (True):
            # check owner: to be implemented
            post.update_one({"_id":post_id }, {"$pull":{"post_comments":{"_id":comment_id}}})
            return comment_id
        else:
            return None

    def upvote_comment(self, upvoterid: ObjectId, upvoter: str,  post_id: ObjectId, comment_id: ObjectId):
        """
        Upvotes a comment. Rescinds the upvote if the user already upvoted it.

        Parameters:
         - upvoterid: id of the upvoter
         - upvoter: name of the upvoter

         NOTE: use only boardid or boardname, pass "None" to unused parameters!
         NOTE: use only upvoterid or upvotername, pass "None" to unused parameters!
         - post_id: the ID of the post the comment falls under
         - comment_id: the ID of the comment being upvoted
        Return: id of the comment upvoted
        Error: return None
        """
        user = self.db.users
        board = self.db.boards
        post=self.db.posts
        if upvoterid == None:
            u_filter = {"username": upvoter}
        else:
            u_filter = {"_id": upvoterid}
        thecomment = post.find_one({"post_comments._id":comment_id})
        theupvoter = user.find_one(u_filter)
        if (theupvoter != None) and (thecomment != None):
            post.update_one({"post_comments._id":comment_id},{"$push":{"post_comments.$.comment_upvoters":theupvoter["_id"]}})
            post.update_one({"post_comments._id": comment_id},{"$inc": {"post_comments.$.comment_upvotes": 1}})
            return comment_id
        else:
            return None


    def notify_post(self,  post_id: ObjectId):
        user = self.db.users

        post = self.db.posts

        thepost = post.find_one({"_id": post_id})

        if  (thepost != None):
            post.update_one({"_id": post_id}, {"$set": {"post_notified": 1}})
            post.update_one({"_id": post_id}, {"$set": {"post_upvotes": float("inf")}})
            return post_id
        else:
            return None
