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
        dataType: "json",
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
        dataType: "json",
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
    }
    //send POST request to server with parameter
    jQuery.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + "/api/board/create",
        dataType: "json",
        data: data,
        success: success,
        error: error
    });
}
