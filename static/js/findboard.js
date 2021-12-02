$(document).ready(function () {
    if ('content' in document.createElement('template')) {

        let offset = 0;

        // Find parent section and template child to clone
        let header = document.querySelector("#findboard_header");
        let sec = document.querySelector("#findboard_section");
        let template = document.querySelector("#findboard_template");

        // Define success function
        let success = function(data) {
            if (offset === 0) sec.innerHTML = "";
            if (data.length <= 0) {
                // No boards
                //header.appendChild(document.querySelector("#findboard_noboards").content.cloneNode(true));
                $("#noboards_div").show()
            } else {
                $("#noboards_div").hide()
                data.forEach(function(board) {

                    let board_id = board["_id"]["$oid"];

                    let b_succ = function(data) {
                        // Setup board
                        let clone = template.content.cloneNode(true);
                        let title = clone.querySelector("h3");
                        title.innerHTML = data["board_name"];
                        let desc = clone.querySelector("p");
                        desc.innerHTML = data["board_description"];
                        let link = clone.querySelector("a");
                        link.href = "/viewboard.html?board=" + board_id;
                        let btn = clone.querySelector("button");
                        if (data["subscribed"]) {
                            btn.innerHTML = "Subscribed!";
                            btn.disabled = true;
                            btn.style.cursor = "default";
                        } else {
                            btn.addEventListener("click", function() {
                                btn.disabled = true;
                                btn.style.pointerEvents = "none";
                                let btn_success = function(data) {
                                    btn.innerHTML = "Subscribed!";
                                };
                                let btn_error = function(err) {
                                    display_error("An error occurred subscribing: " + get_error(err));
                                    btn.innerHTML = "Error";
                                };
                                subscribe_board(board_id, btn_success, btn_error);
                            });

                        }

                        // Add board to layout
                        sec.appendChild(clone);
                    };

                    let b_error = function(err) {
                        console.log(get_error(err));

                        // Setup board
                        let clone = template.content.cloneNode(true);
                        let title = clone.querySelector("h3");
                        title.innerHTML = "Error";
                        let desc = clone.querySelector("p");
                        desc.innerHTML = "An error occurred fetching this board information";
                        let link = clone.querySelector("a");
                        link.href = "/viewboard.html?board=" + board_id;

                        // Add board to layout
                        sec.appendChild(clone);
                    };

                    fetch_board(board_id, b_succ, b_error);

                });
            }
        };

        // Define error function
        let error = function(err) {
            console.log(get_error(err));
            display_error("An error occurred fetching boards: " + get_error(err));
        };

        function do_search() {
            let query = document.getElementById("board-search-query").value;
            if (query === "") query = ".*";
            else {
                // Construct regex using all search words
                query = "(" + query.split(" ").join("|") + ")"
            }

            fetch_boards(query, offset, success, error);
        }

        document.getElementById("submit-board-search").addEventListener("click", function () {
            offset = 0;
            do_search();
        });

        document.getElementById("board-search-query").addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                offset = 0;
                do_search();
            }
        });

        // Do board fetch
        do_search();
    }
});
