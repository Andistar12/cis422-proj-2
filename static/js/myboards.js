$(document).ready(function () {
    if ('content' in document.createElement('template')) {

        // Find parent section and template child to clone
        let header = document.querySelector("#header_section");
        let sec = document.querySelector("#myboard_section");
        let template = document.querySelector("#myboard_template")

        // Define success function
        let success = function(data) {
            if (data.length <= 0) {
                // No boards
                header.appendChild(document.querySelector("#myboard_noboards").content.cloneNode(true));
            } else {
                data.forEach(function(board) {
                    let board_id = board["board_id"];

                    // Setup board
                    let clone = template.content.cloneNode(true);
                    let title = clone.querySelector("h3");
                    title.innerHTML = board["board_name"];
                    let desc = clone.querySelector("p");
                    desc.innerHTML = board["board_description"];
                    let link = clone.querySelector("a");
                    link.href = "/viewboard.html?board=" + board_id;
                    let btn = clone.querySelector("button");
                    btn.addEventListener("click", function() {
                        btn.disabled = true;
                        btn.style.pointerEvents = "none";
                        let btn_success = function() {
                            btn.innerHTML = "Unsubscribed!";
                        };
                        let btn_error = function(err) {
                            console.log(err);
                            display_error("An error occurred subscribing. Reload the page?");
                            btn.innerHTML = "Error";
                        };
                        unsubscribe_board(board_id, btn_success, btn_error);
                    });

                    // Add board to layout
                    sec.appendChild(clone);
                });
            }
        };

        // Define error function
        let error = function(err) {
            console.log(err);
            display_error("An error occurred fetching boards. Reload the page?");
        };

        // Do board fetch
        fetch_user_boards(success, error);
    }
});
