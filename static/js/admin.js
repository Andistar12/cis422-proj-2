$(document).ready(function () {

    document.getElementById("add-admin").addEventListener("click", function () {
        let succ = function () {
            refreshAdmins();
            display_info("Administrator added.");
        }
        let error = function (err) {
            display_error("Failed to add administrator: " + get_error(err))
        }
        add_admin(document.getElementById("input-admin").value, succ, error);
    });

    document.getElementById("rem-admin").addEventListener("click", function () {
        let succ = function () {
            refreshAdmins();
            display_info("Administrator removed.");
        }
        let error = function (err) {
            display_error("Failed to remove administrator: " + get_error(err))
        }
        remove_admin(document.getElementById("input-admin").value, succ, error);
    });

    function refreshAdmins() {
        let succ = function (data) {
            document.getElementById("adminm-list").innerHTML = data;
        }
        let error = function (err) {
            display_error("Failed to refresh admins list: " + get_error(err))
            document.getElementById("adminm-list").innerHTML = "Error occurred getting admins";
        }
        fetch_admins(succ, error);
    }

    document.getElementById("delete-board").addEventListener("click", function () {
        let succ = function () {
            display_info("Board removed.");
        }
        let error = function (err) {
            display_error("Failed to remove board: " + get_error(err));
        }
        delete_board(document.getElementById("board-input-id").value, succ, error);
    });

    document.getElementById("delete-post").addEventListener("click", function () {
        let succ = function () {
            display_info("Post removed.");
        }
        let error = function (err) {
            console.log(get_error(err));
            display_error("Failed to remove post: " + get_error(err));
        }
        delete_post(document.getElementById("board-input-id").value, document.getElementById("post-input-id").value, succ, error);
    });

    document.getElementById("delete-comment").addEventListener("click", function () {
        let succ = function () {
            display_info("Comment removed.");
        }
        let error = function (err) {
            console.log(err);
            display_error("Failed to remove comment: " + get_error(err));
        }
        delete_comment(document.getElementById("post-input-id").value, document.getElementById("comment-input-id").value, succ, error);
    });

    document.getElementById("refresh-admin").addEventListener("click", refreshAdmins);

    refreshAdmins();
});
