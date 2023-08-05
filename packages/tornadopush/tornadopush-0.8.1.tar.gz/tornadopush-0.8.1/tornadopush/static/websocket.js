if (typeof(tornadopush) === 'undefined') {
    var tornadopush = {};
}

(function(tp) {
    
    tp.WebSocket = function(url, protocols) {
        protocols = protocols || [];

        this.successfulConnections = 0;
        this.reconnectInterval = 1000;
        this.reconnectDecay = 1.5;
        this.reconnectAttempts = 0;
        this.timeoutInterval = 2000;

        var self = this;
        var ws;
        var forcedClose = false;
        var timedOut = false;
        
        this.url = url;
        this.protocols = protocols;
        this.readyState = WebSocket.CONNECTING;
        this.URL = url; // Public API

        this.onopen = function(event) {
        };

        this.onclose = function(event) {
        };

        this.onconnecting = function(closeEvent, timedOut) {
        };

        this.onmessage = function(event) {
        };

        this.onerror = function(event) {
        };

        function connect(reconnectAttempt) {
            ws = new WebSocket(url, protocols);
            
            if(!reconnectAttempt) {
                self.onconnecting();
            }
            
            var localWs = ws;
            var timeout = setTimeout(function() {
                timedOut = true;
                if (localWs.readyState !== WebSocket.CLOSED) {
                    localWs.close();
                }
                timedOut = false;
            }, self.timeoutInterval);
            
            ws.onopen = function(event) {
                clearTimeout(timeout);
                self.readyState = WebSocket.OPEN;
                self.successfulConnections += 1;
                self.reconnectAttempts = 0;
                self.onopen(event);
            };
            
            ws.onclose = function(event) {
                clearTimeout(timeout);
                ws = null;
                if (forcedClose) {
                    self.readyState = WebSocket.CLOSED;
                    self.onclose(event);
                } else {
                    self.readyState = WebSocket.CONNECTING;
                    self.reconnectAttempts++;
                    var reconnect = self.onconnecting(event, timedOut);
                    if (reconnect !== false) {
                        setTimeout(function() {
                            connect(true);
                        }, self.reconnectInterval * Math.pow(self.reconnectDecay, self.reconnectAttempts - 1));
                    }
                }
            };
            ws.onmessage = function(event) {
                self.onmessage(event);
            };
            ws.onerror = function(event) {
                self.onerror(event);
            };
        }

        connect(false);

        this.send = function(data) {
            if (ws) {
                return ws.send(data);
            } else {
                throw 'INVALID_STATE_ERR : Pausing to reconnect websocket';
            }
        };

        this.close = function() {
            forcedClose = true;
            if (ws) {
                ws.close();
            }
        };

        /**
         * Additional public API method to refresh the connection if still open (close, re-open).
         * For example, if the app suspects bad data / missed heart beats, it can try to refresh.
         */
        this.refresh = function() {
            if (ws) {
                ws.close();
            }
        };
    };

})(tornadopush);

// Forked from ReconnectingWebSocket:
// MIT License:
//
// Copyright (c) 2010-2012, Joe Walnes
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.