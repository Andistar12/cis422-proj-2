$(document).ready(function () {
    if ('content' in document.createElement('template')) {
        let board_id = new URLSearchParams(window.location.search).get("board");

        if (board_id === null) {
            display_error("An error occurred displaying boards. No board was found");
        } else {
            // Find parent section and template child to clone
            let sec = document.querySelector("#boardpost_section");
            let template = document.querySelector("#boardpost_template");

            // Board information
            let posts = [];
            let board_members = 0;

            let display_posts = function() {
                sec.innerHTML = "";
                if (posts.length === 0) {
                    sec.appendChild(document.querySelector("#boardpost_noposts").content.cloneNode(true));
                } else {
                    posts.forEach(function(post) {
                        let showNotif = document.getElementById("show-notified");
                        let showNotNotif = document.getElementById("show-unnotified");

                        let is_notified = post["post_notified"];
                        if ((is_notified && showNotif.checked) || (!is_notified && showNotNotif.checked)) {

                            let post_id = post["_id"]["$oid"];

                            let clone = template.content.cloneNode(true);
                            let title = clone.querySelector("h3");
                            title.innerHTML = post["post_subject"];
                            let desc = clone.querySelector("p");
                            desc.innerHTML = post["post_description"];
                            let link = clone.querySelector("a");
                            link.href = "/viewpost.html?board=" + board_id + "&post=" + post_id;
                            let upp = clone.querySelector("#upvote_percentage");
                            if (post["post_upvotes"] < 0) {
                                upp.innerHTML = "Notified!";
                            } else {
                                upp.innerHTML = Math.round(post["post_upvotes"] / board_members * 100) + "% upvoted";
                            }

                            // Add board to layout
                            sec.appendChild(clone);
                        }
                    });
                }
            };

            let success = function(data) {
                // Setup board information
                document.getElementById("board_name_header").innerHTML = data["board_name"];
                document.getElementById("board_desc_header").innerHTML = data["board_description"];
                document.getElementById("board_vote_threshold").innerHTML = data["board_vote_threshold"] + "% upvote threshold";

                // Global variables
                board_members = data["board_member_count"];
                posts = data["posts"];
                display_posts();

                document.getElementById("board-content").hidden = false;
            };
            let error = function(err) {
                console.log(err);
                display_error("An error occurred displaying boards. Try refreshing?");
            };

            // Fetch posts
            fetch_board(board_id, success, error);

            // Setup UI elements
            document.getElementById("create-new-post").addEventListener("click", function () {
                window.location.href = $SCRIPT_ROOT + "/makepost.html?board=" + board_id;
            });
            document.getElementById("show-notified").addEventListener("click", display_posts);
            document.getElementById("show-unnotified").addEventListener("click", display_posts);
        }
    }
});
