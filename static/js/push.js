
function urlB64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}


let is_subscribed = false;
let sw_reg = null;


function update_button() {
    // Updates the push button to either enable or disable notifications

	let push_button = document.getElementById("push-button");

	if (Notification.permission === 'denied') {
        // User rejected request
		push_button.textContent = 'Notifications Blocked';
		push_button.disabled = true;
		return;
	}

	if (is_subscribed) {
		// Not yet subscribed
		push_button.textContent = 'Disable Notifications';
	} else {
		// Subscribed
		push_button.textContent = 'Enable Notifications';
	}

	push_button.disabled = false;
}


function update_subscription_on_server(subscription) {
	// Sends the subscription to the server

	$.ajax({
		type:"POST",
		url: $SCRIPT_ROOT + "/push/subscription",
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		async: true,
		data: JSON.stringify({"subscription_token": subscription}),
		success: function(response) {
			console.log("Subscription accepted");
		},
		error: function(err) {
			console.log("Server sent status " + err.status);
		}
	})
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
			console.log('User is subscribed.');
			update_subscription_on_server(subscription);
			is_subscribed = true;
			update_button();
		})
		.catch(function(err) {
			console.log('Failed to subscribe the user: ', err);
			update_button();
		});
}


function unsubscribe_user() {
	// Unsubscribes the user from getting notifications

	sw_reg.pushManager.getSubscription()
		.then(function(subscription) {
			if (subscription) {
				return subscription.unsubscribe();
			}
		})
		.catch(function(error) {
			console.log('Error unsubscribing', error);
		})
		.then(function() {
			update_subscription_on_server(null);
			console.log('User is unsubscribed.');
			is_subscribed = false;
			update_button();
		});
}


function init_push() {
	// Initiates the push button and fetches the application service ID

	let push_button = document.getElementById("push-button");

	// Setup push button listener
	push_button.addEventListener('click', function() {
		push_button.disabled = true;
		if (is_subscribed) {
			unsubscribe_user();
		} else {
			subscribe_user();
		}
	});

	// Set the initial subscription value
	sw_reg.pushManager.getSubscription()
		.then(function(subscription) {
			is_subscribed = !(subscription === null);

			//update_subscription_on_server(subscription);

			if (is_subscribed) {
				console.log('User IS subscribed.');
			} else {
				console.log('User is NOT subscribed.');
			}

			update_button();
		});

	// Fetches the application server's VAPID public key
	$.ajax({
		type:"GET",
		url: $SCRIPT_ROOT + "/push/subscription",
		success: function(response) {
			console.log("Subscription key response",response);
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
		}).catch(function(error) {
			console.error('Service Worker Error', error);
		});
	});
} else {
	console.warn('Push is not supported');
	push_button.textContent = 'Notifications not supported';
}
