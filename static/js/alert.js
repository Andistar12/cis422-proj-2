// Handles creating notifications to alert the user of messages

function display_error(message) {
    // Find parent section and template child to clone
    let sec = document.querySelector("#alert-section");
    let template = document.querySelector("#alert-error");

    // Setup message
    let clone = template.content.cloneNode(true);
    let msg = clone.querySelector("#alert-message-span");
    msg.innerHTML = message;

    // Add to layout
    sec.appendChild(clone);
}

function display_warning(message) {
    // Find parent section and template child to clone
    let sec = document.querySelector("#alert-section");
    let template = document.querySelector("#alert-warning");

    // Setup message
    let clone = template.content.cloneNode(true);
    let msg = clone.querySelector("#alert-message-span");
    msg.innerHTML = message;

    // Add to layout
    sec.appendChild(clone);
}

function display_info(message) {
    // Find parent section and template child to clone
    let sec = document.querySelector("#alert-section");
    let template = document.querySelector("#alert-info");

    // Setup message
    let clone = template.content.cloneNode(true);
    let msg = clone.querySelector("#alert-message-span");
    msg.innerHTML = message;

    // Add to layout
    sec.appendChild(clone);
}