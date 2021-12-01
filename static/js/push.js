
function urlB64ToUint8Array(base64String) {
    // Converts a VAPID key to an array of unit8 bytes

    // Prep string
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');

	// Declare output
	const rawData = window.atob(base64);
  	const outputArray = new Uint8Array(rawData.length);

	// Do conversion
	for (let i = 0; i < rawData.length; ++i) {
		outputArray[i] = rawData.charCodeAt(i);
	}
	return outputArray;
}

// Whether the user is currently subscribed
let is_subscribed = false;

// Holds the service worker object
let sw_reg = null;

function update_button() {
    // Updates the push button to either enable or disable notifications

	let push_button = document.getElementById("push-button")
	let push_button_mobile = document.getElementById("push-button-mobile");

	if (sw_reg == null) {
		// Push notifications not available
        is_subscribed = false;
		if (push_button) {
            push_button.textContent = 'Notifications Not Supported';
            push_button.removeEventListener("click", toggle_notifs);
        }
        if (push_button_mobile) {
            push_button_mobile.textContent = 'Notifications Not Supported';
            push_button_mobile.removeEventListener("click", toggle_notifs);
        }
		return;
	}

	if (Notification.permission === 'denied') {
        // User rejected request
        is_subscribed = false;
        if (push_button) {
            push_button.textContent = 'Notifications Blocked';
            push_button.removeEventListener("click", toggle_notifs);
        }
        if (push_button_mobile) {
            push_button_mobile.textContent = 'Notifications Blocked';
            push_button_mobile.removeEventListener("click", toggle_notifs);
        }
		return;
	}

	if (is_subscribed) {
		// Not yet subscribed
		if (push_button) push_button.textContent = 'Disable Notifications';
		if (push_button_mobile) push_button_mobile.textContent = 'Disable Notifications';
	} else {
		// Subscribed
		if (push_button) push_button.textContent = 'Enable Notifications';
		if (push_button_mobile) push_button_mobile.textContent = 'Enable Notifications';
	}

	if (push_button) push_button.disabled = false;
	if (push_button_mobile) push_button_mobile.disabled = false;
}


function update_subscription_on_server(subscription, action) {
	// Sends the subscription to the server and whether to subscribe or unsubscribe

	return $.ajax({
		type:"POST",
		url: $SCRIPT_ROOT + "/push/subscription",
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		async: true,
		data: JSON.stringify({"subscription_token": subscription, "action": action}),
		success: function(response) {
			console.log("Subscription update accepted");
		}
	});
}


function subscribe_user() {
    // Sets up the subscription

    // Get server public VAPID key
	const applicationServerPublicKey = localStorage.getItem('applicationServerPublicKey');
	const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);

	// Do the subscription registration
	sw_reg.pushManager.subscribe({
			userVisibleOnly: true,
			applicationServerKey: applicationServerKey
		})
		.then(function(subscription) {
			// Send subscription to server
			display_info("You have successfully enabled notifications.");
			update_subscription_on_server(subscription, "add");
			is_subscribed = true;
			update_button();
		})
		.catch(function(err) {
			console.log('Failed to subscribe the user: ', err);
			display_info("Failed to enabled notifications. Have you granted permission?");
			update_button();
		});
}


function unsubscribe_user() {
	// Unsubscribes the user from getting notifications

	sw_reg.pushManager.getSubscription()
		.then(function(subscription) {
			// First notify server of unsubscription
			if (subscription) update_subscription_on_server(subscription, "remove");

			// Then locally unsubscribe
			if (subscription) subscription.unsubscribe();

			// Finally update UI
			is_subscribed = false;
			display_info("You have successfully disabled notifications.");
			update_button();
		}).catch(function(error) {
			console.log('Error unsubscribing', error);
			display_info("Failed to disable notifications. Try again?");
		});
}

// Toggles whether the user has notifications on or off
function toggle_notifs() {
    if ('PushManager' in window) {
        // Web push feature is available, proceed
        if (is_subscribed) {
            unsubscribe_user();
        } else {
            subscribe_user();
        }
    } else {
        // Push feature not available
        sw_reg = null;
        display_error("Your browser does not support Push Notifications. Please try a different browser or platform.");
        update_button();
    }
}

function init_push() {
	// Initiates the push button and fetches the application service ID

	let push_button = document.getElementById("push-button");
	let push_button_mobile = document.getElementById("push-button-mobile");
	if (push_button === null) return;

	// Setup push button listener
	push_button.addEventListener('click', toggle_notifs);
    push_button_mobile.addEventListener('click', toggle_notifs);

	// Set the initial subscription value
	sw_reg.pushManager.getSubscription()
		.then(function(subscription) {
			is_subscribed = !(subscription === null);

			if (subscription !== null) {
				// Refresh subscription server-side
				update_subscription_on_server(subscription, "refresh");
			}

			update_button();
		});

	// Fetches the application server's VAPID public key
	$.ajax({
		type:"GET",
		url: $SCRIPT_ROOT + "/push/subscription",
		success: function(response) {
			//console.log("Subscription key successfully registered");
			localStorage.setItem('applicationServerPublicKey',response.public_key);
		}
	})
}


if ('serviceWorker' in navigator && 'PushManager' in window) {
	// Setup service worker and push manager

	window.addEventListener('load', function() {
		navigator.serviceWorker.register('static/js/sw.js')
			.then(function(swReg) {
				// Save service worker registration and init the ui
				sw_reg = swReg;
				init_push();

                // Store current username
                sw_reg.active.postMessage(JSON.stringify({key: $USERNAME}));
		}).catch(function(error) {
			console.error('Service Worker Error', error);
		});
	});
} else {
	console.warn('Push is not supported');
	update_button();
}
