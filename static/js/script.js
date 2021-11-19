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

function add_admin(username, success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    data = {username: username};
    //send POST request to server with parameter
    jQuery.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + "/api/admins/add",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        data: data,
        success: success,
        error: error
    });
}

function remove_admin(username, success, error) {
    //use default callbacks if none given
    if (!success) success = printer;
    if (!error) error = printer;
    data = {username: username};
    //send POST request to server with parameter
    jQuery.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + "/api/admins/remove",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        data: data,
        success: success,
        error: error
    });
}
