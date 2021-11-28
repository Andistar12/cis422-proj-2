$(document).ready(function () {

    function refreshAdmins() {
        let succ = function (data) {
            document.getElementById("admin-list").innerHTML = data.join("\n");
        }
        let error = function (err) {
            display_error("Failed to refresh admins list: " + get_error(err))
            document.getElementById("admin-list").innerHTML = "Error occurred getting admins";
        }
        fetch_admins(succ, error);
    }


    document.getElementById("btn-admin-action").addEventListener("click", function() {
        if (document.getElementById("rb-delete-board").checked) {
            // Attempt to delete board
            let succ = function () {
                display_info("Board successfully removed.");
            }
            let error = function (err) {
                display_error("Failed to remove board: " + get_error(err));
            }
            delete_board(document.getElementById("board-input-id").value, succ, error);
        } else if (document.getElementById("rb-delete-post").checked) {
            // Attempt to delete post
            let succ = function () {
                display_info("Post removed.");
            }
            let error = function (err) {
                console.log(get_error(err));
                display_error("Failed to remove post: " + get_error(err));
            }
            delete_post(document.getElementById("board-input-id").value, document.getElementById("post-input-id").value, succ, error);
        } else if (document.getElementById("rb-add-admin").checked) {
            let succ = function () {
                refreshAdmins();
                display_info("Administrator added.");
            }
            let error = function (err) {
                display_error("Failed to add administrator: " + get_error(err))
            }
            add_admin(document.getElementById("admin-input-id").value, succ, error);
        } else if (document.getElementById("rb-remove-admin").checked) {
            let succ = function () {
                refreshAdmins();
                display_info("Administrator removed.");
            }
            let error = function (err) {
                display_error("Failed to remove administrator: " + get_error(err))
            }
            remove_admin(document.getElementById("admin-input-id").value, succ, error);
        } else {
            display_error("An error occurred processing your request. Please refresh the page.");
        }
    });

    document.getElementById("btn-refresh-admins").addEventListener("click", refreshAdmins);

    refreshAdmins();
});
