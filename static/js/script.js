"use strict";

//default callback
//prints all arguments given on one line
function printer(...args) {
    console.log(...args);
}

//fetch up to 50 boards
//takes a search term and an offset - offset=0 produces boards 0-49
//on success, produces an array of board objects
function fetch_boards(search, offset, success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    //put parameters in data object
    var data = {search: search, offset: offset};
    //send GET request to server with parameters
    jQuery.ajax({
        type: "GET",
        url: $SCRIPT_ROOT + "/api/boards",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        data: data,
        success: success,
        error: error
    });
}

//fetch boards current user is subscribed to
//returns an array of board objects
function fetch_user_boards(success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    //send GET request to server
    jQuery.ajax({
        type: "GET",
        url: $SCRIPT_ROOT + "/api/board/user",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: success,
        error: error
    });
}

//returns a list of administrator account names
//only succeeds if called by an admin
function fetch_admins(success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    //send GET request to server with parameters
    jQuery.ajax({
        type: "GET",
        url: $SCRIPT_ROOT + "/api/admins",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: success,
        error: error
    });
}

//adds an existing account as an administrator
//only succeeds if called by an admin
function add_admin(username, success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    var data = {username: username};
    //send POST request to server with parameter
    jQuery.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + "/api/admins/add",
        data: data,
        success: success,
        error: error
    });
}

//removes an account from the administrator list
//only works if called by an admin
function remove_admin(username, success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    var data = {username: username};
    //send POST request to server with parameter
    jQuery.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + "/api/admins/remove",
        data: data,
        success: success,
        error: error
    });
}

//fetches information about a specific board
function fetch_board(board_id, success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    var data = {board_id: board_id};
    //send GET request to server with parameter
    jQuery.ajax({
        type: "GET",
        url: $SCRIPT_ROOT + "/api/board",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        data: data,
        success: success,
        error: error
    });
}

//creates a new board with the given name, description, and threshold
function create_board(name, description, threshold, success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    var data = {
        board_name: name,
        board_description: description,
        board_vote_threshold: threshold
    };
    //send POST request to server with parameter
    jQuery.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + "/api/board/create",
        data: data,
        success: success,
        error: error
    });
}

//subscribes the current user to a board with the given id
function subscribe_board(id, success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    var data = {board_id: id};
    //send POST request to server with parameter
    jQuery.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + "/api/board/subscribe",
        data: data,
        success: success,
        error: error
    });
}

//unsubscribes the current user from a board with the given id
function unsubscribe_board(id, success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    var data = {board_id: id};
    //send POST request to server with parameter
    jQuery.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + "/api/board/unsubscribe",
        data: data,
        success: success,
        error: error
    });
}

//deletes the given board
//must be an administrator to delete a board
function delete_board(id, success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    var data = {board_id: id};
    //send POST request to server with parameter
    jQuery.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + "/api/board/delete",
        data: data,
        success: success,
        error: error
    });
}

//fetches information about a specific post
function fetch_post(board_id, post_id, success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    var data = {board_id: board_id, post_id: post_id};
    //send GET request to server with parameter
    jQuery.ajax({
        type: "GET",
        url: $SCRIPT_ROOT + "/api/post",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        data: data,
        success: success,
        error: error
    });
}

//creates a new post in the given board with the given subject and description
function create_post(board_id, subject, description, success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    var data = {
        board_id: board_id,
        post_subject: subject,
        post_description: description
    };
    //send POST request to server with parameter
    jQuery.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + "/api/post/create",
        data: data,
        success: success,
        error: error
    });
}

//deletes the post in the given board with the given id
function delete_post(board_id, post_id, success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    var data = {
        board_id: board_id,
        post_id: post_id,
    };
    //send POST request to server with parameter
    jQuery.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + "/api/post/delete",
        data: data,
        success: success,
        error: error
    });
}

//upvotes the post in the given board with the given id
function upvote_post(board_id, post_id, success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    var data = {
        board_id: board_id,
        post_id: post_id,
    };
    //send POST request to server with parameter
    jQuery.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + "/api/post/upvote",
        data: data,
        success: success,
        error: error
    });
}

//unupvotes the post in the given board with the given id
function unupvote_post(board_id, post_id, success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    var data = {
        board_id: board_id,
        post_id: post_id,
    };
    //send POST request to server with parameter
    jQuery.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + "/api/post/upvote/cancel",
        data: data,
        success: success,
        error: error
    });
}

//adds a comment to the post in the given board with the given id
function add_comment(board_id, post_id, message, success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    var data = {
        board_id: board_id,
        post_id: post_id,
        message: message
    };
    //send POST request to server with parameter
    jQuery.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + "/api/comment/create",
        data: data,
        success: success,
        error: error
    });
}

//upvotes a given comment
function upvote_comment(post_id, comment_id, success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    var data = {
        post_id: post_id,
        comment_id: comment_id
    };
    //send POST request to server with parameter
    jQuery.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + "/api/comment/upvote",
        data: data,
        success: success,
        error: error
    });
}

//deletes a given comment
function delete_comment(post_id, comment_id, success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    var data = {
        post_id: post_id,
        comment_id: comment_id
    };
    //send POST request to server with parameter
    jQuery.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + "/api/comment/delete",
        data: data,
        success: success,
        error: error
    });
}
