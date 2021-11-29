$(document).ready(function () {

    let board_id = new URLSearchParams(window.location.search).get("board");

    // Update button to link back to correct board
    document.getElementById("board-link").href = "/viewboard.html?board=" + board_id;


    let succ = function(data) {
        // Update board name field, then make page visible
        document.getElementById("board_name").innerHTML = data["board_name"]; 
        document.getElementById("makepost_content").hidden = false;
    }
    let error = function(err) {
        console.log(get_error(err));
    }
    fetch_board(board_id, succ, error);

    document.getElementById("makepost_submit").addEventListener("click", function () {
        let sub = document.getElementById("makepost_subject").value;
        let desc = document.getElementById("makepost_desc").value;

        let success = function(data) {
            window.location.href = $SCRIPT_ROOT + "/viewpost.html?board=" + board_id + "&post=" + data["post_id"];
        }

        let error = function(err) {
            display_error("Error making posting: " + get_error(err));
        }

        create_post(board_id, sub, desc, success, error);
    });
});
