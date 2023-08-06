;(function ($, document, window, undefined) {
    "use strict";

    var pluginName = 'djxami_core';

    var defaults = {
        'url': false,
        'csrf_token': false,
        'mars_read_url': false,
        'stream_url': false,
        'first_query_pause': 1000,
        'queries_interval': 5000,
        'stream_interval': 100,
    };


    function Plugin(options) {
        this.options = $.extend({}, defaults, options)
        this._defaults = defaults;
        this.opts = $.extend(this._defaults, options);
        //this.in_cookies = this.getCookie('djxami')
        this.streams = {}
        this.messages = {}
        this.start();
    }

    Plugin.prototype = {
        start: function () {
            var in_cookies = this.getCookie('djxami')
            if (in_cookies) {
                in_cookies = in_cookies.replace(/"/g, '').split(':').map(Number)
                for (var i in in_cookies) {
                    this.messages[in_cookies[i]] = {}
                }
            }
            var $this = this
            setTimeout(function () {
                this.forceQuery(this.options['first_query_pause'])
                setInterval(function () {
                    this.forceQuery()
                }.bind(this), this.options['queries_interval'])
            }.bind(this))
            //setInterval(function () {
            //    $.getJSON(this.options['url'], function (res) {
            //        res.forEach(function (data) {
            //            if (data['id'] in this.messages) {
            //                return
            //            }
            //            $this.messages[data['id']] = {}
            //            $.event.trigger('djxami:message_' + data['type'], [$this, data])
            //            if (data['stream']) {
            //                $this.startStream(data['id'])
            //            }
            //        })
            //    })
            //}.bind(this), this.options['queries_interval'])
        },
        forceQuery: function () {
            var $this = this
            $.getJSON(this.options['url'], function (res) {
                res.forEach(function (data) {
                    if (data['id'] in $this.messages) {
                        return
                    }
                    $this.messages[data['id']] = {}
                    $.event.trigger('djxami:message_' + data['type'], [$this, data])
                    if (data['stream']) {
                        $this.startStream(data['id'])
                    }
                })
            })
        },
        startStream: function (id, url) {
            var $this = this
            this.streams[id] = setInterval(function () {
                if ('stop' in this.messages[id] && this.messages[id]['stop'] === true) {
                    clearInterval(this.streams[id])
                }
                $.ajax({
                    'url': this.options['stream_url'],
                    'type': 'POST',
                    'data': {'id': id, 'csrfmiddlewaretoken': this.options['csrf_token']},
                    'success': function (data) {
                        $.event.trigger('djxami:stream_' + data['id'], [$this, data])
                    }
                })
            }.bind(this), this.options['stream_interval'])
        },
        getCookie: function (name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },
        mark_as_read: function (id, on_success) {
            var $this = this;
            $.ajax({
                'url': this.options['mars_read_url'],
                'method': 'POST',
                'data': {
                    'id': id,
                    'csrfmiddlewaretoken': this.options['csrf_token']
                },
                'success': function (data) {
                    $this.messages[id]['stop'] = true
                    if (on_success) {
                        on_success($this)
                    }
                }
            })
        }
    };

    $.fn[pluginName] = function (options) {
        return new Plugin(options)
    }


})(jQuery, document, window);