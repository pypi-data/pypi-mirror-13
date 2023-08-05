if (typeof(tornadopush) === 'undefined') {
    var tornadopush = {};
}

(function(tp) {

    tp.DEBUG = false;
    var debug = function(o) {
        if (tp.DEBUG) {
            console.log(o);
        }
    };

    tp.SSEChannelListener = (function() {
        var _ = function(url, presence) {
            this.listeners = {};
            this.url = url;
            this.source = new EventSource(url);
            if (presence) {
                this.enable_presence(presence);
            }
        };

        _.prototype.bind = function(event, callback) {
            if (typeof(event) === 'string') {
                event = [event];
            }
            for (var i = 0; i < event.length; i++) {
                if (!this.listeners[event[i]]) {
                    this.listeners[event[i]] = [];
                    this.source.addEventListener(event[i], this.message_handler.bind(this));
                }
                this.listeners[event[i]].push(callback);
            }
        };

        _.prototype.message_handler = function(e) {
            var sender = e.data.substr(0, e.data.indexOf(';')),
                data = e.data.substr(e.data.indexOf(';') + 1);
            debug("Received event '" + e.type + "' from '" + sender + "'");
            this.dispatch(e.type, tp.decode_data(data), sender);
        };

        _.prototype.dispatch = function(event, data, sender) {
            if (this.listeners[event]) {
                this.listeners[event].forEach(function(cb) {
                    cb(data, event, sender);
                });
            }
        };

        _.prototype.send = function(data) {
            var req = new XMLHttpRequest();
            req.onload = function() {
                debug('Data submitted');
            };
            req.open("POST", this.url, true);
            req.setRequestHeader("Content-Type", "application/json");
            req.send(tp.encode_data(data));
        };

        _.prototype.enable_presence = function(presence) {
            debug("Presence enabled through push channel");
            this.presence = presence;
            var self = this;
            this.source.addEventListener('__presence__', function(e) {
                self.presence.handle_message(e.data);
            });
            return presence;
        };

        _.prototype.close = function() {
            this.source.close();
        };

        return _;
    })();

    tp.WebSocketChannelListener = (function() {
        var _ = function(socket, presence) {
            this.listeners = {};
            this.presence = null;
            this.socket = null;
            if (socket) {
                this.listen(socket);
            }
            if (presence) {
                this.enable_presence(presence);
            }
        };

        _.from_url = function(url, presence) {
            return new _(new tp.WebSocket(url), presence);
        };

        _.prototype.listen = function(socket) {
            this.socket = socket;
            var self = this;
            var prev_handler = this.socket.onmessage;
            this.socket.onmessage = function(e) {
                if (prev_handler) {
                    prev_handler(e);
                }
                self.message_handler(e);
            };
            if (this.presence) {
                this.presence.listen(this.socket);
            }
        };

        _.prototype.message_handler = function(e) {
            if (e.data.substr(0, 6) !== 'event:') {
                return;
            }
            var evt_data = e.data.substr(6),
                meta = evt_data.split(';', 2),
                event = meta[0],
                sender = meta[1],
                data = evt_data.substr(event.length + sender.length + 2);
            debug("Received event '" + event + "' from '" + sender + "'");
            this.dispatch(event, tp.decode_data(data), sender);
        };

        _.prototype.dispatch = function(event, data, sender) {
            if (this.listeners[event]) {
                this.listeners[event].forEach(function(cb) {
                    cb(data, event, sender);
                });
            }
        };

        _.prototype.bind = function(event, callback) {
            if (typeof(event) === 'string') {
                event = [event];
            }
            for (var i = 0; i < event.length; i++) {
                if (!this.listeners[event[i]]) {
                    this.listeners[event[i]] = [];
                }
                this.listeners[event[i]].push(callback);
            }
        };

        _.prototype.send = function(data) {
            this.socket.send("message:" + tp.encode_data(data));
            debug("Data submitted");
        };

        _.prototype.enable_presence = function(presence) {
            debug("Presence enabled through push channel");
            this.presence = presence;
            if (this.socket) {
                presence.listen(this.socket);
            }
            return presence;
        };

        _.prototype.close = function() {
            this.socket.close();
        };

        return _;
    })();

    tp.FallbackChannelListener = (function() {
        var _ = function(channel, presence, enablePresenceOnFallback) {
            this.channel = channel;
            this.presence = presence;
            this.enablePresenceOnFallback = enablePresenceOnFallback;
            this.listener = null;
            this.binds = [];
            this.tryWebSocket();
        };

        _.prototype.onwssuccess = function() {};

        _.prototype.onfallback = function() {};

        _.prototype.tryWebSocket = function() {
            if (this.listener) {
                this.listener.close();
            }
            if (!tp.ws_support) {
                return this.fallback();
            }
            var self = this;
            var qs = this.presence ? '?presence=1' : '';
            var url = tp.wsurl(tp.path(this.channel) + qs);
            var ws = new tp.WebSocket(url);
            ws.onconnecting = function(closeEvent, timedOut) {
                if ((closeEvent || timedOut) && self.shouldFallback(ws, closeEvent, timedOut)) {
                    self.fallback();
                    return false;
                }
            };
            ws.onopen = function() {
                self.setupListener(new tp.WebSocketChannelListener(ws, self.presence));
                self.onwssuccess(self.listener);
            };
        };

        _.prototype.shouldFallback = function(ws, closeEvent, timedOut) {
            return timedOut || (!ws.successfulConnections && [1002, 1003, 1006].indexOf(closeEvent.code) !== -1);
        };

        _.prototype.fallback = function() {
            console.log('WebSocket connection cannot be initialized, falling back to SSE');
            var qs = this.presence || this.enablePresenceOnFallback ? '?presence=1' : '';
            var url = tp.url(tp.path(this.channel, true) + qs);
            this.setupListener(new tp.SSEChannelListener(url, this.presence));
            this.onfallback(this.listener);
        };

        _.prototype.isUsingWebSocket = function() {
            return this.listener && (this.listener instanceof tp.WebSocketChannelListener);
        };

        _.prototype.setupListener = function(listener) {
            this.listener = listener;
            for (var i = 0; i < this.binds.length; i++) {
                listener.bind(this.binds[i][0], this.binds[i][1]);
            }
        };

        _.prototype.bind = function(event, callback) {
            this.binds.push([event, callback]);
            if (this.listener) {
                return this.listener.bind(event, callback)
            }
        };

        _.prototype.send = function(data) {
            if (this.listener) {
                return this.listener.send(data)
            }
        };

        _.prototype.dispatch = function(event, data) {
            if (this.listener) {
                return this.listener.dispatch(event, data)
            }
        };

        _.prototype.enable_presence = function(presence) {
            this.presence = presence;
            if (this.listener) {
                return this.listener.enable_presence(presence);
            }
        };

        _.prototype.close = function() {
            if (this.listener) {
                return this.listener.close()
            }
        };

        return _;
    })();

    tp.init = function (hostname, secured) {
        if (typeof(hostname) === 'undefined' && typeof(TORNADOPUSH_HOSTNAME) !== 'undefined') {
            hostname = TORNADOPUSH_HOSTNAME;
        }
        if (typeof(secured) === 'undefined' && typeof(TORNADOPUSH_SECURED) !== 'undefined') {
            secured = TORNADOPUSH_SECURED;
        }
        tp.hostname = hostname || 'localhost:8888';
        tp.secured = secured || false;
        tp.ws_support = typeof(WebSocket) !== 'undefined';
        if (typeof(TORNADOPUSH_TOKEN) !== 'undefined') {
            tp.authentify(TORNADOPUSH_TOKEN);
        }
    };

    tp.authentify = function(token) {
        tp.auth_token = token;
    };

    tp.decode_data = function(data) {
        if (!data) {
            return null;
        }
        return JSON.parse(data);
    };

    tp.encode_data = function(data) {
        if (typeof(data) === 'string') {
            return data;
        }
        return JSON.stringify(data);
    };

    tp.url = function(path, scheme) {
        scheme = scheme || (tp.secured ? 'https://' : 'http://');
        var url = scheme + tp.hostname + path;
        if (tp.auth_token) {
            url +=  (path.indexOf('?') > -1 ? '&' : '?')
                 + 'token=' + encodeURIComponent(tp.auth_token);
        }
        return url;
    };

    tp.wsurl = function(path) {
        return tp.url(path, (tp.secured ? 'wss://' : 'ws://'));
    };

    tp.path = function(channel, sse) {
        if (!channel) {
            throw Error("Missing channel name");
        }
        var path = '/channel/' + channel;
        if (sse) {
            path += '.sse';
        }
        return path;
    };

    tp.subscribe = function (channel, presence, enablePresenceOnFallback) {
        if (!tp.hostname) {
            tp.init();
        }
        if (presence && typeof(presence) === 'boolean') {
            if (typeof(tp.Presence) === 'undefined') {
                console.error('Presence cannot be enabled through push channel because of missing libs');
            } else {
                presence = new tp.Presence(null, channel);
            }
        }
        return new tp.FallbackChannelListener(channel, presence, enablePresenceOnFallback);
    };

})(tornadopush);