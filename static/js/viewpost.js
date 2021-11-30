$(document).ready(function () {
    if ('content' in document.createElement('template')) {
        let board_id = new URLSearchParams(window.location.search).get("board");
        let post_id = new URLSearchParams(window.location.search).get("post");

        if (board_id === null || post_id === null) {
            display_error("An error occurred displaying the post. No post was found");
        } else {

            // Update button to link back to correct board
            document.getElementById("board-link").href = "/viewboard.html?board=" + board_id;

            let error = function(err) {
                console.log(get_error(err));
                display_error("An error occurred fetching the post. Try refreshing?");
            };

            let success = function(post_data) {

                let succ2 = function(board_data) {
                    // Update post-related UI
                    document.getElementById("post-subject").innerHTML = post_data["post_subject"];
                    document.getElementById("post-username").innerHTML = post_data["post_username"];
                    document.getElementById("post-description").innerHTML = post_data["post_description"];
                    let post_date = new Date(post_data["post_date"]["$date"]); // Assume server time uses UTC
                    document.getElementById("post-date").innerHTML = post_date.toLocaleDateString("en-us") + " " + post_date.toLocaleTimeString("en-us");

                    // Update board-related UI
                    document.getElementById("board-name").innerHTML = board_data["board_name"];

                    // Update UI based on notified status
                    if (post_data["post_notified"]) {
                        // Has already been notified. Delete UI elements
                        let pup = document.getElementById("post-upvote-percent-parent");
                        pup.parentNode.removeChild(pup);
                        pup = document.getElementById("post-upvote-count-parent");
                        pup.parentNode.removeChild(pup);

                        let btn = document.getElementById("post-upvote");
                        btn.innerHTML = "Already notified!";
                        btn.disabled = true;
                        btn.style.cursor = "default";
                    } else {
                        let upvotes_raw = post_data["post_upvotes"];
                        let board_members = board_data["board_member_count"];
                        let upp = Math.round(upvotes_raw / board_members * 100) + "%";
                        document.getElementById("post-upvote-count").innerHTML = upvotes_raw;
                        document.getElementById("post-upvote-percent").innerHTML = upp;

                        let btn = document.getElementById("post-upvote");
                        if (post_data["upvoted"]) {
                            btn.innerHTML = "Upvoted!";
                            btn.style.cursor = "default";
                            btn.disabled = true;
                        } else {
                            btn.addEventListener("click", function() {
                                let succ3 = function() {
                                    let upp = Math.round((upvotes_raw+1) / board_members * 100) + "%";
                                    document.getElementById("post-upvote-count").innerHTML = upvotes_raw + 1;
                                    document.getElementById("post-upvote-percent").innerHTML = upp;
                                    btn.innerHTML = "Upvoted!";
                                    btn.style.cursor = "default";
                                    btn.disabled = true;
                                }
                                let error2 = function(err) {
                                    console.log(err);
                                    display_error("An error occurred upvoting the post. Try again?");
                                }
                                upvote_post(board_id, post_id, succ3, error2);
                            });
                        }
                    }

                    // Finally make page visible
                    document.getElementById("post-content").hidden = false;

                }

                fetch_board(board_id, succ2, error);
            };
            
            // Fetch posts
            fetch_post(board_id, post_id, success, error);
        }
    }
});
