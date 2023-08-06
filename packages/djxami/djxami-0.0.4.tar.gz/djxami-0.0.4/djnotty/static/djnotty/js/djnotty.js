$(function () {

    $.noty.defaults = {
        layout: 'topCenter',
        theme: 'relax', // or 'relax'
        type: 'information',
        dismissQueue: true, // If you want to use queue feature set this true
        template: '<div class="noty_message"><span class="noty_text"></span><div class="noty_close"></div></div>',
        animation: {
            open: {height: 'toggle'}, // or Animate.css class names like: 'animated bounceInLeft'
            close: {height: 'toggle'}, // or Animate.css class names like: 'animated bounceOutLeft'
            easing: 'swing',
            speed: 500 // opening & closing animation speed
        },
        timeout: false, // delay for closing event. Set false for sticky notifications
        force: false, // adds notification to the beginning of queue when set to true
        modal: false,
        maxVisible: 10, // you can set max visible notification for dismissQueue true option,
        killer: false, // for close all notifications before show
        closeWith: ['click'], // ['click', 'button', 'hover', 'backdrop'] // backdrop click will close all notifications
        callback: {
            onShow: function () {
            },
            afterShow: function () {
            },
            onClose: function () {
            },
            afterClose: function () {
            },
            onCloseClick: function () {
            },
        },
    };
    window.notty_scripts = {
        'djnotty_linked': function (djxami_core, opts, data) {

            opts['callback'] = {
                'onClose': function () {
                    window.location = opts['linked']
                }
            }

            return opts
        },
        'djnotty_close': function (djxami_core, opts, data) {
            console.log(djxami_core)
            opts['callback'] = {
                'onClose': function () {
                    if ('redirect' in opts) {
                        clb = function (djxami_core) {
                            console.log(data)
                            window.location = data['opts']['redirect']
                        }
                    }
                    else {
                        clb = false;
                    }
                    djxami_core.mark_as_read(data['id'], clb)
                }
            }

            return opts
        },
        'djnotty_progressbar': function (djxami_core, opts, data) {
            $(document).bind('djxami:stream_' + data['id'], function (e, djxami_core, data) {
                var n = djxami_core.messages[data['id']]['djnoty']
                n.setText(data['opts']['text'])
                if (n.$bar !== undefined) {
                    n.$bar.find('.progress-bar').attr('aria-valuenow', data['opts']['current']).css('width', data['opts']['current'] + '%');
                }
            })
        }
    }
    $(document).bind('djxami:message_djnotty', function (e, djxami_core, data) {
        var opts = data['opts']
        if (!opts) {
            opts = {}
        }

        if (data['scripts']) {
            data['scripts'].forEach(function (script) {
                if (script in window.notty_scripts) {
                    opts = $.extend(opts, window.notty_scripts[script](djxami_core, opts, data))
                }
            })
        }
        djxami_core.messages[data['id']]['djnoty'] = noty(opts);

    })


})