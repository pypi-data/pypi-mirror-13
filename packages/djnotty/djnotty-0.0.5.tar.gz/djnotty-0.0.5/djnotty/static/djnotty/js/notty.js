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
    window.notty_builders = {
        'djnotty_linked': function (opts, data) {
            opts['callback'] = {
                'onClose': function () {
                    window.location = opts['linked']
                }
            }

            return opts
        },
        'djnotty_close': function (opts, data) {
            opts['callback'] = {
                'onClose': function () {
                    $.ajax({
                        'url': opts['url'],
                        'method': 'POST',
                        'data': {
                            //*3
                            'id': data['id'],
                            'csrfmiddlewaretoken': window['csrf_token'] === undefined ? getCookie('csrftoken') : csrf_token
                        },
                        'success': function () {
                            if ('linked' in opts) {
                                window.location = opts['linked']
                            }
                        }
                    })
                }
            }

            return opts
        }
    }
    //var ids = getCookie('djnotty').split(',')
    var in_cookies = getCookie('djnotty')
    if (in_cookies) {
        var ids = in_cookies.replace(/"/g, '').split(':').map(Number);
    }
    else {
        var ids = []
    }
    setInterval(function () {
        $.getJSON(djnotty_url, function (res) {
            res.forEach(function (data) {
                console.log(data['id'])
                if (ids.indexOf(data['id']) > -1) {
                    return
                }
                ids.push(data['id'])
                try {
                    var opts = data['opts']
                    if (!opts) {
                        opts = {}
                    }

                    data['builders'].forEach(function (builder) {
                        opts = window.notty_builders[builder](opts, data)
                    })
                    noty(opts);
                } catch (e) {
                    console.info('Cant show noty. ' + e)
                }
            })
        })
    }, 1000)


    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
})