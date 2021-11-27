/*
 Copyright 2016 Google Inc. All Rights Reserved.
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
 http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 */

// Names of the two caches used in this version of the service worker.
// Change to v2, etc. when you update any of the local resources, which will
// in turn trigger the install event again.
const PRECACHE = 'precache-v1';
const RUNTIME = 'runtime';
const USERNAME_CACHE = 'username_cache_req';

// A list of local resources we always want to be cached.
const PRECACHE_URLS = [ ];

// The install handler takes care of precaching the resources we always need.
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(PRECACHE)
      .then(cache => cache.addAll(PRECACHE_URLS))
      .then(self.skipWaiting())
  );
});

// The activate handler takes care of cleaning up old caches.
self.addEventListener('activate', event => {
  const currentCaches = [PRECACHE, RUNTIME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return cacheNames.filter(cacheName => !currentCaches.includes(cacheName));
    }).then(cachesToDelete => {
      return Promise.all(cachesToDelete.map(cacheToDelete => {
        return caches.delete(cacheToDelete);
      }));
    }).then(() => self.clients.claim())
  );
});

// The fetch handler serves responses for same-origin resources from a cache.
// If no response is found, it populates the runtime cache with the response
// from the network before returning it to the page.
self.addEventListener('fetch', event => {
  // Skip cross-origin requests, like those for Google Analytics.
  if (event.request.url.startsWith(self.location.origin)) {
    event.respondWith(
      caches.match(event.request).then(cachedResponse => {
        if (cachedResponse) {
          return cachedResponse;
        }

        return caches.open(RUNTIME).then(cache => {
          return fetch(event.request).then(response => {
            // Put a copy of the response in the runtime cache.
            return cache.put(event.request, response.clone()).then(() => {
              return response;
            });
          });
        });
      })
    );
  }
});

const swBroadcastChannel = new BroadcastChannel("swbc");
swBroadcastChannel.onmessage = function(event) {
    // Setup database
    let db_req = indexedDB.open(USERNAME_CACHE, 1);
    db_req.onupgradeneeded = function(event) {
        var db = event.target.result;
        db.createObjectStore(USERNAME_CACHE);
    };

    // On open, add username to "username" key of USERNAME_CACHE object store of db
    db_req.onsuccess = function(event2) {
        let db = event2.target.result;
        let transaction = db.transaction([USERNAME_CACHE], "readwrite");
        let objstore = transaction.objectStore(USERNAME_CACHE);
        objstore.put(event.data.key, "username"); // Fail silently
    }
}

// Setup the service worker to receive push notifications
self.addEventListener('push', function(event) {
    let data = JSON.parse(event.data.text());

    // Open DB
    let db_req = indexedDB.open(USERNAME_CACHE, 1);
    db_req.onupgradeneeded = function(event) {
        var db = event.target.result;
        db.createObjectStore(USERNAME_CACHE);
    };

    // On open, add username to "username" key of USERNAME_CACHE object store of db
    db_req.onsuccess = function(event2) {
        let db = event2.target.result;
        let transaction = db.transaction([USERNAME_CACHE], "readonly");
        let objstore = transaction.objectStore(USERNAME_CACHE);
        let req = objstore.get("username");
        req.onsuccess = function(event3) {
            let cached_username = req.result;

            // Check username match against notification
            if (data["username"] === cached_username) {
                // This is actually for us
                const title = data["board_name"];
                let msg = data["message"];

                // Construct destination URL
                let board_id = data["board_id"]["$oid"];
                let post_id = data["post_id"]["$oid"];
                let url = "/viewpost.html?board=" + board_id + "&post=" + post_id;

                const options = {
                    body: msg,
                    icon: '/images/svg-seeklogo.com.svg',
                    badge: '/images/svg-seeklogo.com.svg',
                    data: {
                        url: url
                    }
                };

                event.waitUntil(self.registration.showNotification(title, options));
            }
        };
    }
});

// Handle the user interacting with the notification
self.addEventListener('notificationclick', function(e) {
    var notification = e.notification;
    var url = notification.data.url;
    var action = e.action;

    if (action !== 'close') {
        clients.openWindow(url);
    }
    notification.close();
});

