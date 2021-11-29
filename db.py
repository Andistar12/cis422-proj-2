"""
Handles all database transactions.

The database has a number of MongoDB collections:
 - users: contains information about users
 - admins: contains information about system administrators
 - boards: contains information about boards
 - comments: contains posts id and comments

In the users collection, each user entry has the following form:
{   "_id": id of user
    "username": username of the person. This is the unique identifier for the user
    "password": hashed password of the user
    "subscriptions": list of board IDs
    "admin": whether the user is an administrator
    "notification": info about the user's notification
    "user_date": creation date of user
    "last_active_date": last active date
    "boards_owned": the board id of the board that the user made
    "posts_owned": the posts id of the post that the user posted

}

In the admins collection, each admin entry has the following form:
{
    "_id": id of admins collection
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
    "board_posts": actual posts without comments
    "finished_posts": past notified posts


}

In a particular board's collection, each entry is a post which has the following form:
{
    "_id": unique ID of the board
    "post_subject": subject of the post
    "post_description": description of the post
    "post_owner": owner id of the post
    "post_date": creation date of the post
    "post_upvotes": number of upvotes on the post
    "post_upvoters": list of user IDs who voted on the post
    "post_notified": whether the post notification has already been triggered
    "comments_container": contariner id in which the container stores the comments
    "last_active_date": last active date

}

container Level (in comments collection):
{
    "_id": id used by the comment collection (container id)
    "post_id": id of the post of the comments they belong to
    "comments": actual comments
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
import re
import datetime
from datetime import timedelta
from pymongo import MongoClient
from bson.objectid import ObjectId



class AppDB:
    """
    The manager for all database transactions
    """

    def __init__(self,client):
        """
        Initiates the AppDB manager

        Parameters:
         - client: the MongoDB client
        """
        self.client = client
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
                         "notification":[],
                         "user_date":datetime.datetime.now(),
                         "last_active_date":None,
                         "boards_owned":[],
                         "posts_owned":[]})
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
        admin=self.db.admins
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
            if val["admin"]==1:
                admin.delete_one({"userid":val["_id"]})
            return val["_id"]
        else:
            return None

    def change_username(self, userid: ObjectId, user_name: str, new_username: str):
        """
        Removes a user from the database if exists

        Parameters:
         - userid: the id of the user
         - username: the username of the user to remove
         NOTE: use only userid or username, pass "None" to unused parameters!
        Return: An object of ID (created by MongoDB) of user changed
        Error: return None
        """
        user=self.db.users
        admin=self.db.admins
        if userid==None:
            filter={"username":user_name}
        else:
            filter={"_id":userid}
        val=user.find_one(filter)
        check=user.find_one({"_id":new_username})
        if val != None and check==None:
            user.update_one(filter,{"$set":{"username":new_username}})
            if val["admin"]==1:
                admin.update_one({"userid":val["_id"]},{"$set":{"username":new_username}})
            return val["_id"]
        else:
            return None

    def change_password(self, userid: ObjectId, user_name: str, new_password: str):
        """
        Removes a user from the database if exists

        Parameters:
         - userid: the id of the user
         - username: the username of the user to remove
         NOTE: use only userid or username, pass "None" to unused parameters!
        Return: An object of ID (created by MongoDB) of user changed
        Error: return None
        """
        user=self.db.users
        admin=self.db.admins
        if userid==None:
            filter={"username":user_name}
        else:
            filter={"_id":userid}
        val=user.find_one(filter)
        if val != None:
            user.update_one(filter,{"$set":{"password":new_password}})

            return val["_id"]
        else:
            return None

    def add_notification(self, userid: ObjectId, user_name: str, notification: dict):
        """

         Parameters:
                 - userid: the id of the user
                 - username: the username of the administrator
                NOTE: use only userid or username, pass "None" to unused parameters!
                Return: user id of notification info added
                Error: return None
        """
        user = self.db.users
        if userid==None:
            filter={"username":user_name}
        else:
            filter={"_id":userid}
        theuser=user.find_one(filter)
        if theuser!=None:
            user.update_one(filter,{"$push":{"notification":notification}})
            return theuser["_id"]
        else:
            return None

    def remove_notification(self, userid: ObjectId, user_name: str, notification: dict):
        """
         Parameters:
                 - userid: the id of the user
                 - username: the username of the administrator
                NOTE: use only userid or username, pass "None" to unused parameters!
                Return: user id of notification info added
                Error: return None
        """
        user = self.db.users
        if userid == None:
            filter = {"username": user_name}
        else:
            filter = {"_id": userid}
        theuser = user.find_one(filter)
        if theuser != None:
            user.update_one(filter, {"$pull": {"notification": notification}})
            return theuser["_id"]
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
        check=admin.find_one(filter)

        if (val!=None) and (check==None):
            if val["admin"]!=1:
                user.update_one({"userid": val["_id"]},{"$set":{"admin":1}})
                admin.insert_one({"username":val["username"],
                                  "userid":val["_id"]})
                return admin.find_one({"username":val["username"]})["_id"]
            else:
                return admin.find_one({"username":val["username"]})["_id"]
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
         - An array of dictionaries containing information about administrators
         Error: return empty array
        """
        admin=self.db.admins
        return list(admin.find())


    def fetch_boards(self, keyword: str, offset: int, include_posts: bool):
        """
        Returns up to 50 boards. The ordering of the boards may be catered to the user
        - Posts are not included
        Parameters:
         - keyword: a search string to filter results by
         - offset: offset into board results. For example, an offset of 1 will
                    return boards 50 through 99
         -include_post: option to include posts
        Returns:
         - An array of dictionaries, each dictionary containing information about a board
        Error: return empty array
        """
        board=self.db.boards
        regx=re.compile(keyword,re.IGNORECASE)
        if include_posts:
            array = list(board.find({"$or": [{"board_name": regx},
                                             {"board_description": regx}]}))
        else:
            array=list(board.find({"$or":[{"board_name":regx},
                                            {"board_description":regx}]},{"board_posts":-1}))

        return array[offset*50:(offset+1)*50]

    def fetch_board(self, boardid: ObjectId):
        """
        Fetches information about a single board.

        Parameters:
         - boardid: the unique board ID

        Return: dictionary containing board information
        Error: return empty dictionary
        """
        board=self.db.boards
        filter = {"_id": boardid}
        val = board.find_one(filter)
        if val != None:
            board.update_one(filter, {"$push": {"board_posts": {"$each": [], "$sort": {"post_notified":-1, "post_upvotes": -1}}}})
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

        if board.find_one({"board_name":boardname})!=None:
            return None

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
                                "board_posts":[],
                                "finished_posts":[]})

            board_id=board.find_one({"board_name":boardname})["_id"]
            user.update_one(filter, {"$push": {"boards_owned":board_id}})
            return board_id
        else:
            return None

    def delete_board(self, operator_id: ObjectId, operator: str, boardid: ObjectId):
        """
        Deletes a board from the database.

        All users are automatically unsubscribed from the deleted board.
        This is expensive operation
        Parameters:
         - operator_id : id of the operator
         - operator : name of the operator
         NOTE: use only operator_id or operator, pass "None" to unused parameters!
         - boardid: the board ID to delete

        Return: the id of board deleted
        Error: return None
        """
        board = self.db.boards
        user = self.db.users
        admin = self.db.admins
        comment = self.db.comments
        filter = {"_id": boardid}
        val = board.find_one(filter)
        if operator_id != None:
            u_filter = {"_id": operator_id}
        else:
            u_filter = {"username": operator}
        theuser = user.find_one(u_filter)
        if val != None and theuser != None:

            if (admin.find_one({"userid": theuser["_id"]}) != None):
                board.delete_one(filter)
                member = val["board_members"]
                posts = val["board_posts"]
                for post in posts:
                    comment.delete_one({"_id": post["comments_container"]})

                for uid in member:
                    user.update_one({"_id": uid}, {"$pull": {"subscriptions": val["_id"]}})

                user.update_one({"_id": val["board_owner"]}, {"$pull": {"boards_owned": val["_id"]}})
                return val["_id"]
        else:
            return None

    def change_boardname(self, operator_id: ObjectId, operator: str, boardid: ObjectId, new_boardname: str):
        """
        Deletes a board from the database.

        All users are automatically unsubscribed from the deleted board.
        This is expensive operation
        Parameters:
         - operator_id : id of the operator
         - operator : name of the operator
         NOTE: use only operator_id or operator, pass "None" to unused parameters!
         - boardid: the board ID to change

        Return: the id of board changed
        Error: return None
        """
        board = self.db.boards
        user = self.db.users
        admin = self.db.admins

        filter = {"_id": boardid}
        val = board.find_one(filter)
        if operator_id != None:
            u_filter = {"_id": operator_id}
        else:
            u_filter = {"username": operator}
        theuser = user.find_one(u_filter)
        if val != None and theuser != None:

            if (admin.find_one({"userid": theuser["_id"]}) != None) or (val["board_owner"]==theuser["_id"]):
                board.update_one(filter,{"$set":{"board_name":new_boardname}})
                return val["_id"]
        else:
            return None

    def change_boardowner(self, operator_id: ObjectId, operator: str, boardid: ObjectId, new_ownerid: ObjectId):
        """
        Deletes a board from the database.

        All users are automatically unsubscribed from the deleted board.
        This is expensive operation
        Parameters:
         - operator_id : id of the operator
         - operator : name of the operator
         NOTE: use only operator_id or operator, pass "None" to unused parameters!
         - boardid: the board ID to change

        Return: the id of board changed
        Error: return None
        """
        board = self.db.boards
        user = self.db.users
        admin = self.db.admins

        filter = {"_id": boardid}
        val = board.find_one(filter)
        if operator_id != None:
            u_filter = {"_id": operator_id}
        else:
            u_filter = {"username": operator}
        theuser = user.find_one(u_filter)
        if val != None and theuser != None:

            if (admin.find_one({"userid": theuser["_id"]}) != None) or (val["board_owner"]==theuser["_id"]):
                board.update_one(filter,{"$set":{"board_owner":new_ownerid}})
                return val["_id"]
        else:
            return None

    def change_votethreshold(self, operator_id: ObjectId, operator: str, boardid: ObjectId, new_threshold: int):
        """
        Deletes a board from the database.

        All users are automatically unsubscribed from the deleted board.
        This is expensive operation
        Parameters:
         - operator_id : id of the operator
         - operator : name of the operator
         NOTE: use only operator_id or operator, pass "None" to unused parameters!
         - boardid: the board ID to change

        Return: the id of board changed
        Error: return None
        """
        board = self.db.boards
        user = self.db.users
        admin = self.db.admins

        filter = {"_id": boardid}
        val = board.find_one(filter)
        if operator_id != None:
            u_filter = {"_id": operator_id}
        else:
            u_filter = {"username": operator}
        theuser = user.find_one(u_filter)
        if val != None and theuser != None:

            if (admin.find_one({"userid": theuser["_id"]}) != None) or (val["board_owner"]==theuser["_id"]):
                board.update_one(filter,{"$set":{"board_vote_threshold":new_threshold}})
                return val["_id"]
        else:
            return None

    def change_boarddescription(self, operator_id: ObjectId, operator: str, boardid: ObjectId, new_description: str):
        """
        Deletes a board from the database.

        All users are automatically unsubscribed from the deleted board.
        This is expensive operation
        Parameters:
         - operator_id : id of the operator
         - operator : name of the operator
         NOTE: use only operator_id or operator, pass "None" to unused parameters!
         - boardid: the board ID to change

        Return: the id of board changed
        Error: return None
        """
        board = self.db.boards
        user = self.db.users
        admin = self.db.admins

        filter = {"_id": boardid}
        val = board.find_one(filter)
        if operator_id != None:
            u_filter = {"_id": operator_id}
        else:
            u_filter = {"username": operator}
        theuser = user.find_one(u_filter)
        if val != None and theuser != None:

            if (admin.find_one({"userid": theuser["_id"]}) != None) or (val["board_owner"]==theuser["_id"]):
                board.update_one(filter,{"$set":{"board_description":new_description}})
                return val["_id"]
        else:
            return None


    def purge_boards(self, day: int):
        """
        Purges all boards with no activity in recent time.

        All users are automatically unsubscribed from the deleted boards.

        This is an very expensive operation.

        Parameters:
         - days: boards older than "days" day will be deleted
        Return: list of id of boards deleted
        Error: No error
        """
        board = self.db.boards
        user = self.db.users
        comment = self.db.comments
        boards = list(board.find())
        ret=[]
        for b in boards:
            if datetime.datetime.now()-b["board_date"]>timedelta(days=day):
                member = b["board_members"]
                posts = b["board_posts"]
                board_id=b["_id"]
                for post in posts:
                    comment.delete_one({"_id":post["comments_container"]})

                for uid in member:
                    user.update_one({"_id": uid}, {"$pull": {"subscriptions": b["_id"]}})

                user.update_one({"_id":b["board_owner"]},{"$pull":{"boards_owned":b["_id"]}})
                ret.append(board_id)
                return ret


    def subscribe_board(self, userid: ObjectId, user_name: str, boardid: ObjectId):
        """
        Subscribes a user to a board.

        Parameters:
         - userid: the id of the user
         - user_name: the user that is subscribing
         NOTE: use only userid or user_name, pass "None" to unused parameters!
         - boardid: the ID of the board the user is subscribing to

         Return: subscribed board id
         Error: return None
        """
        user = self.db.users
        board = self.db.boards
        if userid == None:
            u_filter = {"username": user_name}
        else:
            u_filter = {"_id": userid}
        b_filter = {"_id": boardid}
        theuser = user.find_one(u_filter)
        theboard = board.find_one(b_filter)
        if (theuser!=None):
            if (boardid in theuser["subscriptions"]):
                return theboard["_id"]
            elif (theboard != None):
                user.update_one(u_filter, {"$push": {"subscriptions": theboard["_id"]}})
                board.update_one(b_filter, {"$push": {"board_members": theuser["_id"]}})
                board.update_one(b_filter, {"$inc": {"board_member_count": 1}})
                return theboard["_id"]
            else:
                return None
        else:
            return None
    def unsubscribe_board(self, userid: ObjectId, user_name: str, boardid: ObjectId):
        """
        Unsubscribes a user to a board.

        Parameters:
        - userid: the id of the user
        - user_name: the user that is subscribing
        - board_id: the ID of the board the user is subscribing to

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
        b_filter = {"_id": boardid}
        theuser = user.find_one(u_filter)
        theboard = board.find_one(b_filter)
        if theuser!=None:
            if (boardid not in theuser["subscriptions"]):
                return theboard["_id"]
            elif (theboard != None):
                user.update_one(u_filter, {"$pull": {"subscriptions": theboard["_id"]}})
                board.update_one(b_filter, {"$pull": {"board_members": theuser["_id"]}})
                board.update_one(b_filter, {"$inc": {"board_member_count": -1}})
                return theboard["_id"]
            else:
                return None
        else:
            return None

    def fetch_post(self, boardid: ObjectId, post_id: ObjectId):
        """
        Fetches all information about a single post.

        NOTE: Doesn't contain comments! Call "fetch_comments()" to get sorted comments!

        Parameters:
         - board_id: the ID of the board the post belongs under
         - boardname: name of the board
         - post_id: the ID of the post to fetch
        NOTE: use only boardid or boardname, pass "None" to unused parameters!

        Returns:
         -  A dictionaries of posts
        Error:return empty dictionary
        """

        board=self.db.boards
        thepost=board.find_one({"_id":boardid, "board_posts._id":post_id})

        if (thepost!=None) :
            return board.find_one({"_id":boardid, "board_posts._id":post_id},{"board_posts.$":1})["board_posts"][0]
        else:
            return {}

    def moveto_finishedpost(self, boardid: ObjectId):
        """
        Move all notified posts in a board to the finished posts

        Parameters:
         - board_id: the ID of the board the post belongs under

        Returns: A array of id of posts moved
        Error:return None
        """

        board=self.db.boards
        theboard=board.find_one({"_id":boardid})
        if (theboard!=None) :
            ret=[]
            posts=board.find_one({"_id":boardid})["board_posts"]
            for post in posts:
                if post["post_notified"]==1:
                    board.update_one({"_id":boardid},{"$push":{"finished_posts":post}})
                    board.update_one({"_id":boardid},{"$pull":{"board_posts":{"_id":post["_id"]}}})
                    ret.append(post["_id"])
            return ret
        else:
            return None

    def create_post(self, ownerid: ObjectId, owner: str, boardid: ObjectId,  subject: str, description: str):
        """
        Creates a post

        The creation date of the post is set to now.

        Parameters:
         - ownerid: the user id who is creating the post
         - owner: owner of the post
         - board_id: the ID of the board the post belongs under

         NOTE: use only ownerid or owner, pass "None" to unused parameters!

         - subject: the subject of the post
         - description: the description of the post
        Returns:
         - The unique ID of the new post
        Error: return None
        """
        user=self.db.users
        board=self.db.boards
        comment=self.db.comments
        b_filter={"_id":boardid}
        if ownerid==None:
            o_filter={"username":owner}
        else:
            o_filter={"_id":ownerid}
        theowner=user.find_one(o_filter)
        theboard=board.find_one(b_filter)
        if (theowner!=None) and (theboard!=None):
            if (theboard["_id"] in theowner["subscriptions"]):
                post_id = ObjectId()
                comment.insert_one({"post_id": post_id,
                                    "comments": []})
                container_id=comment.find_one({"post_id": post_id})["_id"]
                board.update_one(b_filter,{"$push":{"board_posts":{"_id":post_id,
                                                            "post_subject":subject,
                                                            "post_description":description,
                                                            "post_owner":theowner["_id"],
                                                            "post_date":datetime.datetime.now(),
                                                            "post_upvotes":0,
                                                            "post_upvoters":[],
                                                            "post_notified":0,
                                                            "comments_container":container_id,
                                                            "last_active_date":None}}})


                user.update_one({"_id":theowner["_id"]},{"$push":{"posts_owned":post_id}})
                return post_id
            else:
                return None
        else:
            return None

    def delete_post(self, operator_id: ObjectId, operator: str,  boardid: ObjectId, post_id: ObjectId):
        """
        Deletes a post.

        Parameters:
         - operator_id: id of the operator
         - operator: name of the operator

         NOTE: use only operator_id or operator, pass "None" to unused parameters!

         - post_id: the ID of the post to delete
         Return: the id of deleted post
         Error: return None
        """
        user = self.db.users
        board=self.db.boards
        admin=self.db.admins
        comment=self.db.comments
        p_filter={"_id":boardid,"board_posts._id":post_id}
        if operator_id == None:
            o_filter = {"username": operator}

        else:
            o_filter = {"_id": operator_id}
        theoperator = user.find_one(o_filter)
        thepost = board.find_one(p_filter)
        if thepost!=None:
            theownerid = board.find_one(p_filter,{"board_posts.$":1})["board_posts"][0]["post_owner"]
        else:
            return None
        if theoperator!=None:
            if ((theoperator["_id"] ==theownerid) or (admin.find_one({"userid":theoperator["_id"]})!=None)) :
                    board.update_one(p_filter,{"$pull":{"board_posts":{"_id":post_id}}})
                    user.update_one({"_id":theownerid},{"$pull":{"posts_owned":post_id}})
                    comment.delete_one({"post_id":post_id})
                    return post_id
            else:
                return None
        else:
            return None

    def upvote_post(self, upvoterid: ObjectId, upvoter: str, boardid: ObjectId, post_id: ObjectId):
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
        board=self.db.boards
        p_filter={"_id":boardid,"board_posts._id":post_id}
        if upvoterid == None:
            u_filter = {"username": upvoter}
        else:
            u_filter = {"_id": upvoterid}
        thepost = board.find_one(p_filter,{"board_posts.$":1})["board_posts"][0]
        theupvoter = user.find_one(u_filter)
        if thepost!=None and theupvoter!=None:
            if (thepost["post_notified"]==0) and (theupvoter["_id"] not in thepost["post_upvoters"]):
                board.update_one(p_filter, {"$push":{"board_posts.$.post_upvoters":theupvoter["_id"]}})
                board.update_one(p_filter, {"$inc": {"board_posts.$.post_upvotes": 1}})
                board.update_one(p_filter, {"$set": {"board_posts.$.last_active_date":datetime.datetime.now()}})
                return post_id
            else:
                return None
        else:
            return None

    def unupvote_post(self, upvoterid: ObjectId, upvoter: str, boardid: ObjectId, post_id: ObjectId):
        """
        Rescinds an upvote given to a post

        Parameters:
         - upvoter id: id of the upvoter
         - upvoter: name of the upvoter

         NOTE: use only upvoterid or upvotername, pass "None" to unused parameters!
         - post_id: the ID of the post to un-upvote
         Return: id of post un-upvoted
         Error: Return None
        """
        user = self.db.users
        board=self.db.boards
        p_filter={"_id":boardid,"board_posts._id":post_id}
        if upvoterid == None:
            u_filter = {"username": upvoter}
        else:
            u_filter = {"_id": upvoterid}
        thepost = board.find_one(p_filter,{"board_posts.$":1})["board_posts"][0]
        theupvoter = user.find_one(u_filter)
        if thepost!=None and theupvoter!=None:
            if (thepost["post_notified"]==0) and (theupvoter["_id"] in thepost["post_upvoters"]):
                board.update_one(p_filter, {"$pull":{"board_posts.$.post_upvoters":theupvoter["_id"]}})
                board.update_one(p_filter, {"$inc": {"board_posts.$.post_upvotes": -1}})

                return post_id
            else:
                return None
        else:
            return None

    def purge_posts(self,  board_id: str, day: int):
        """
        Purges all posts older than a given number of days.

        Parameters:

         - board_id: the ID of the board to purge
         - days: the posts with the inactive days longer than this many days will be deleted
         Return: array of id of posts deleted
         Error: return None
        """
        board=self.db.boards
        admin=self.db.admins
        user=self.db.users
        comment=self.db.comments
        ret=[]

        b_filter={"_id":board_id}

        theboard=board.find_one(b_filter)
        if theboard!=None:
            posts=theboard["board_posts"]
            for post in posts:
                if datetime.datetime.now()-post["last_active_date"]>timedelta(days=day):
                    post_id=post["_id"]
                    post_owner=post["post_owner"]
                    board.update_one({"_id":board_id,"board_posts._id":post_id},{"$pull":{"board_posts":{"_id":post_id}}})
                    user.update_one({"_id": post_owner}, {"$pull": {"posts_owned": post_id}})
                    comment.delete_one({"post_id": post_id})
                    ret.append(post_id)
            return ret
        else:
            return None

    def add_comment(self, ownerid: ObjectId, owner: str,  boardid: ObjectId, post_id: ObjectId,  message: str):
        """
        Adds a comment to a post.

        Parameters:
         - ownerid: id of the owner
         - owner: name of the owner

         NOTE: use only ownerid or owner, pass "None" to unused parameters!

         - post_id: the ID of the post the comment falls under
         - message: the message content of the comment
         Return: id of the comment added
         Error: return None
        """
        user = self.db.users
        comment=self.db.comments
        board=self.db.boards
        p_filter={"_id":boardid,"board_posts._id":post_id}
        if ownerid == None:
            o_filter = {"username": owner}
        else:
            o_filter = {"_id": ownerid}
        theowner = user.find_one(o_filter)
        thepost = board.find_one(p_filter)
        if (theowner != None) and (thepost != None):
            comment_id=ObjectId()
            comment.update_one({"_id":post_id}, {"$push": {"comments":
                                                                {"_id":comment_id,
                                                                "comment_owner":theowner["_id"],
                                                                "comment_message":message,
                                                                "comment_date":datetime.datetime.now(),
                                                                "comment_upvotes":0,
                                                                "comment_upvoters":[]}}})
            board.update_one(p_filter, {"$set": {"board_posts.$.last_active_date": datetime.datetime.now()}})
            return comment_id
        else:
            return None

    def delete_comment(self, operator_id: ObjectId, operator: str,  post_id: ObjectId, comment_id: ObjectId):
        """
        Removes a comment from a post.

        Parameters:
         - operator_id: id of the operator
         - operator: name of the operator
         - post_id: id of the post it belongs to
         NOTE: use only operatorid or operator, pass "None" to unused parameters!

         - comment_id: id of the comment
         Return: id of the comment deleted
         Error: return None
        """

        user = self.db.users
        admin = self.db.admins
        comment=self.db.comments
        c_filter={"post_id":post_id,"comments._id":comment_id }
        if operator_id == None:
            o_filter = {"username": operator}

        else:
            o_filter = {"_id": operator_id}
        theoperator = user.find_one(o_filter)
        thecomment = comment.find_one(c_filter)
        if thecomment!=None:
            theownerid = comment.find_one(c_filter, {"comments.$": 1})["comments"][0]["comment_owner"]
        else:
            return None
        if theoperator!=None:
            if  ((theoperator["_id"] == theownerid) or (admin.find_one({"userid": theoperator["_id"]}) != None)):
                comment.update_one(c_filter, {"$pull":{"comments":{"_id":comment_id}}})
                return comment_id
            else:
                return None
        else:
            return None

    def change_comment(self, operator_id: ObjectId, operator: str,  post_id: ObjectId, comment_id: ObjectId, new_comment: str):
        """
        Removes a comment from a post.

        Parameters:
         - operator_id: id of the operator
         - operator: name of the operator
         - post_id: id of the post it belongs to
         NOTE: use only operatorid or operator, pass "None" to unused parameters!

         - comment_id: id of the comment
         Return: id of the comment changed
         Error: return None
        """

        user = self.db.users
        admin = self.db.admins
        comment=self.db.comments
        c_filter={"post_id":post_id,"comments._id":comment_id }
        if operator_id == None:
            o_filter = {"username": operator}

        else:
            o_filter = {"_id": operator_id}
        theoperator = user.find_one(o_filter)
        thecomment = comment.find_one(c_filter)
        if thecomment!=None:
            theownerid = comment.find_one(c_filter, {"comments.$": 1})["comments"][0]["comment_owner"]
        else:
            return None
        if theoperator!=None:
            if  ((theoperator["_id"] == theownerid) or (admin.find_one({"userid": theoperator["_id"]}) != None)):
                comment.update_one(c_filter, {"$set":{"comments.$.comment_message":new_comment}})
                return comment_id
            else:
                return None
        else:
            return None

    def upvote_comment(self, upvoterid: ObjectId, upvoter: str, post_id: ObjectId,  comment_id: ObjectId):
        """
        Upvotes a comment. Rescinds the upvote if the user already upvoted it.

        Parameters:
         - upvoterid: id of the upvoter
         - upvoter: name of the upvoter
         - post_id: id of the post it belongs to
         NOTE: use only boardid or boardname, pass "None" to unused parameters!

         - comment_id: the ID of the comment being upvoted
        Return: id of the comment upvoted
        Error: return None
        """
        user = self.db.users
        board = self.db.boards
        comment=self.db.comments
        c_filter={"_id":post_id,"comments._id":comment_id}
        if upvoterid == None:
            u_filter = {"username": upvoter}
        else:
            u_filter = {"_id": upvoterid}
        thecomment = comment.find_one(c_filter)
        theupvoter = user.find_one(u_filter)
        if (thecomment != None):
            theupvoters= comment.find_one(c_filter, {"comments.$": 1})["comments"][0]["comment_upvoters"]
        else:
            return None
        if theupvoter!=None:
            if theupvoter["_id"] not in theupvoters:
                comment.update_one(c_filter,{"$push":{"comments.$.comment_upvoters":theupvoter["_id"]}})
                comment.update_one(c_filter,{"$inc": {"comments.$.comment_upvotes": 1}})
                return comment_id
            else:
                return None
        else:
            return None

    def unupvote_comment(self, upvoterid: ObjectId, upvoter: str, post_id: ObjectId,  comment_id: ObjectId):
        """
        Upvotes a comment. Rescinds the upvote if the user already upvoted it.

        Parameters:
         - upvoterid: id of the upvoter
         - upvoter: name of the upvoter
         - post_id: id of the post it belongs to
         NOTE: use only boardid or boardname, pass "None" to unused parameters!

         - comment_id: the ID of the comment being upvoted
        Return: id of the comment upvoted
        Error: return None
        """
        user = self.db.users
        board = self.db.boards
        comment=self.db.comments
        c_filter={"_id":post_id,"comments._id":comment_id}
        if upvoterid == None:
            u_filter = {"username": upvoter}
        else:
            u_filter = {"_id": upvoterid}
        thecomment = comment.find_one(c_filter)
        theupvoter = user.find_one(u_filter)
        if (thecomment != None):
            theupvoters= comment.find_one(c_filter, {"comments.$": 1})["comments"][0]["comment_upvoters"]
        else:
            return None
        if theupvoter!=None:
            if theupvoter["_id"] in theupvoters:
                comment.update_one(c_filter,{"$pull":{"comments.$.comment_upvoters":theupvoter["_id"]}})
                comment.update_one(c_filter,{"$inc": {"comments.$.comment_upvotes": -1}})
                return comment_id
            else:
                return None
        else:
            return None


    def fetch_comments(self, post_id: ObjectId):
        comment=self.db.comments
        c_filter={"post_id":post_id}
        thecomment=comment.find_one(c_filter)
        if thecomment!=None:
            comment.update_one(c_filter,{"$push": {"comments": {"$each": [], "$sort": {"comment_upvotes": -1}}}})
            return comment.find_one(c_filter)["comments"]
        else:
            return None

    def notify_post(self, boardid: ObjectId, post_id: ObjectId):
        user = self.db.users
        board=self.db.boards

        p_filter={"_id": boardid, "board_posts._id":post_id}
        thepost = board.find_one(p_filter)

        if  (thepost != None):
            board.update_one(p_filter, {"$set": {"board_posts.$.post_notified": 1}})
            board.update_one(p_filter, {"$set": {"board_posts.$.post_upvotes": -1}})
            return post_id
        else:
            return None
