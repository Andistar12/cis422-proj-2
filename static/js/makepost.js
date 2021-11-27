$(document).ready(function () {
    document.getElementById("makepost_submit").addEventListener("click", function () {
        let board_id = new URLSearchParams(window.location.search).get("board");
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
