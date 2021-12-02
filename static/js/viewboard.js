$(document).ready(function () {
    if ('content' in document.createElement('template')) {
        let board_id = new URLSearchParams(window.location.search).get("board");
        let subscribed = false;

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
                            let title = clone.querySelector("#post_title");
                            title.innerHTML = post["post_subject"];
                            let post_date = new Date(post["post_date"]["$date"]); // Assume server time uses UTC
                            let dt = clone.querySelector("#creation_date");
                            dt.innerHTML = post_date.toLocaleDateString("en-us") + " " + post_date.toLocaleTimeString("en-us");
                            let link = clone.querySelector("#post_link");
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

            let btn = document.getElementById("subscribe");
            let update_subscribe_btn = function() {
                if (subscribed) btn.innerHTML = "Unsubscribe";
                else btn.innerHTML = "Subscribe";
            }

            btn.addEventListener("click", function() {
                btn.disabled = true;
                if (subscribed) {
                    // Attempt to unsubscribe
                    let btn_success = function() {
                        subscribed = false;
                        update_subscribe_btn();
                        btn.disabled = false;
                    };
                    let btn_error = function(err) {
                        console.log(err);
                        display_error("An error occurred unsubscribing. Reload the page?");
                        btn.innerHTML = "Error";
                    };
                    unsubscribe_board(board_id, btn_success, btn_error);
                } else {
                    // Attempt to unsubscribe
                    let btn_success = function() {
                        subscribed = true;
                        update_subscribe_btn();
                        btn.disabled = false;
                    };
                    let btn_error = function(err) {
                        console.log(err);
                        display_error("An error occurred subscribing. Reload the page?");
                        btn.innerHTML = "Error";
                    };
                    subscribe_board(board_id, btn_success, btn_error);
                }
            });

            let success = function(data) {
                // Setup board information
                document.getElementById("board_name_header").innerHTML = data["board_name"];
                document.getElementById("board_desc_header").innerHTML = data["board_description"];
                subscribed = data["subscribed"];
                update_subscribe_btn();
                let vote = document.getElementById("board_vote_threshold");
                vote.innerHTML = data["board_vote_threshold"] + "% upvote threshold | " + data["board_member_count"] + " members";

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
