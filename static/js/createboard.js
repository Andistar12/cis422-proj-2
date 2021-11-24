$(document).ready(function () {
    document.getElementById("submit-board").addEventListener("click", function() {
        let succ = function(data) {
            let board_id = data.board_id;
            let btn_success = function(data) {
                window.location.href = $SCRIPT_ROOT + "/viewboard.html?board=" + board_id;
            };
            let btn_error = function() {
                display_error("The board has been created, but an error occurred subscribing you to it");
            };
            subscribe_board(board_id, btn_success, btn_error);
        }
        let err = function(err) {
            display_error("Error creating board: " + get_error(err));
        }
        display_info("Creating board...");
        create_board(document.getElementById("board-name").value, document.getElementById("board-desc").value, document.getElementById("board-threshold").value, succ, err);
    });
});
