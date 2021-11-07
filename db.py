"""
Handles all database transactions.

The database has a number of MongoDB collections:
 - users: contains information about users
 - admins: contains information about system administrators
 - boards: contains information about boards
 - [board_id]: contains posts and comments in a particular board

In the users collection, each user entry has the following form:
{
    "username": username of the person. This is the unique identifier for the user
    "password": hashed password of the user
    "subscriptions": list of board IDs
    "admin": whether the user is an administrator
}

In the admins collection, each admin entry has the following form:
{
    "username": username of the person. This is the unique identifier for the administrator
}

In the boards collection, each board entry has the following form:
{
    "board_id": unique ID of the board
    "board_name": name of the board
    "board_description": description of the board
    "board_date": creation date of the board
    "board_member_count": number of members on the board
    "board_members": list of members in the board
    "board_vote_threshold": the percentage of community required for vote
}

In a particular board's collection, each entry is a post which has the following form:
{
    "post_id": unique ID of the board
    "post_subject": subject of the post
    "post_description": description of the post
    "post_username": username of the post owner
    "post_date": creation date of the post
    "post_upvotes": number of upvotes on the post
    "post_upvoters": list of user IDs who voted on the post
    "post_notified": whether the post notification has already been triggered
    "post_comments": list of comments dictionaries (see below)
}

Comments has the following form:
{
    "comment_id": unique ID of the comment
    "comment_username": name of the comment owner
    "comment_message": message content of the comment
    "comment_date": creation date of the comment
    "comment_upvotes": number of raw upvotes on the comment
    "comment_upvoters": list of user IDs who voted on the comment 
}

"""

import pymongo

class AppDB:
    """
    The manager for all database transactions
    """

    def __init__(self, client: pymongo.MongoClient):
        """
        Initiates the AppDB manager

        Parameters:
         - client: the MongoDB client
        """
        self.client = client

    def fetch_user(self, username: str):
        """
        Returns information about a user if exists

        Parameters:
         - username: the username of the user
        Returns:
         - A dictionary container the user information, or an empty dictionary otherwise
        """
        pass # TODO

    def add_user(self, username: str, password: str):
        """
        Adds a user to the database
        
        Parameters:
         - username: the username to use
         - password: the hashed password to use
        """
        pass # TODO

    def remove_user(self, username: str):
        """
        Removes a user from the database if exists

        Parameters:
         - username: the username of the user to remove
        """
        pass # TODO

    def add_admin(self, username: str):
        """
        Adds an administrator to the system. This has no effect if the user is already an administrator

        Parameters:
         - username: the username of the administrator
        """
        pass # TODO

    def remove_admin(self, username: str):
        """
        Removes an administrator from the system.

        Parameters:
         - username: the username of the administrator to remove
        """
        pass # TODO

    def fetch_admins(self):
        """
        Fetches all admins of the system.

        Parameters:
         - None
         Returns:
         - An array of dictionaries, each dictionary containing information about an administrator
        """
        pass # TODO

    def fetch_boards(self, search: str, offset: int):
        """
        Returns up to 50 boards.

        Parameters:
         - search: a search string to filter results by
         - offset: offset into board results. For example, an offset of 1 will
                    return boards 50 through 99
        Returns:
         - An array of dictionaries, each dictionary containing information about a board
        """
        pass # TODO

    def fetch_board(self, board_id: str):
        """
        Fetches information about a single board.

        Posts will be sorted in the following order:
         - Any post that has been notified should be first
         - Then sort by number of upvotes in decreasing order

        Parameters:
         - board_id: the unique board ID
        """
        pass # TODO

    def create_board(self, name: str, desc: str, vote_threshold: int):
        """
        Creates a new board and assigns it a unique ID. 

        The creation date of the board is set to now.

        Parameters:
         - name: the name of the board
         - desc: the description of the board
         - vote_threshold: the vote threshold for the board
        Returns:
         - The unique ID of the new board, or None if an error occurs
        """
        pass # TODO

    def delete_board(self, board_id: str):
        """
        Deletes a board from the database.

        All users are automatically unsubscribed from the deleted board.

        Parameters:
         - board_id: the board ID to delete
        """
        pass # TODO

    def purge_boards(self, days: int):
        """
        Purges all boards with no activity in recent time.

        All users are automatically unsubscribed from the deleted boards.

        This is an expensive operation.

        Parameters:
         - days: the number of days from today by which boards should be deleted.
                Posts older than "days" days from today should be deleted
        """
        pass # TODO

    def subscribe_board(self, username: str, board_id: str):
        """
        Subscribes a user to a board. Unsubscribes if the user is subscribed.

        Parameters:
         - username: the user that is subscribing
         - board_id: the ID of the board the user is subscribing to
        """
        pass # TODO

    def fetch_post(self, board_id: str, post_id: str, include_comments: bool):
        """
        Fetches all information about a single post.

        Comments will be sorted by upvote in descreasing order.

        Parameters:
         - board_id: the ID of the board the post belongs under
         - post_id: the ID of the post to fetch
         - include_comments: whether post_comments should be included
        Returns:
         - An array of dictionaries, each representing a post
        """
        pass # TODO

    def create_post(self, board_id: str, username: str, subject: str, description: str):
        """
        Creates a post

        The creation date of the post is set to now.

        Parameters:
         - board_id: the ID of the board the post belongs under
         - username: the username who is creating the post
         - subject: the subject of the post
         - description: the description of the post
        Returns:
         - The unique ID of the new post, or None if an error occurs
        """
        pass # TODO

    def delete_post(self, board_id: str, post_id: str):
        """
        Deletes a post.

        Parameters:
         - board_id: the ID of the board the post belongs under
         - post_id: the ID of the post to delete
        """
        pass # TODO

    def upvote_post(self, board_id: str, post_id: str, username: str):
        """
        Upvotes a post. Rescinds the upvote if the user already upvoted it.

        Parameters:
         - board_id: the ID of the board the post belongs under
         - post_id: the ID of the post to upvote
         - username: the user doing the upvote
        """
        pass # TODO

    def purge_posts(self, board_id: str, days: int):
        """
        Purges all posts older than a given number of days.

        This is an expensive operation.

        Parameters:
         - board_id: the ID of the board to purge
         - days: the number of days from today by which posts should be deleted.
                Posts older than "days" days from today should be deleted
        """
        pass # TODO

    def add_comment(self, board_id: str, post_id: str, username: str, message: str):
        """
        Adds a comment to a post.

        Parameters:
         - board_id: the ID of the board the post belongs under
         - post_id: the ID of the post the comment falls under
         - username: the username of the user creating it
         - message: the message content of the comment
        """
        pass # TODO

    def delete_comment(self, board_id: str, post_id: str, comment_id: str):
        """
        Removes a comment from a post.

        Parameters:
         - board_id: the ID of the board the post belongs under
         - post_id: the ID of the post the comment falls under
         - comment_id: the ID of the comment to delete
        """
        pass # TODO

    def upvote_comment(self, board_id: str, post_id: str, comment_id: str, username: str):
        """
        Upvotes a comment. Rescinds the upvote if the user already upvoted it.

        Parameters:
         - board_id: the ID of the board the post belongs under
         - post_id: the ID of the post the comment falls under
         - comment_id: the ID of the comment being upvoted
         - username: the user doing the upvote
        """
        pass # TODO
