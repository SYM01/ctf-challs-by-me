var refreshCaptcha = function() {
    this.src = '/captcha?t=' + (new Date()).getTime();
};

var fetchAction = function(endpoint, method) {
    return function(id) {
        fetch("/" + endpoint + "/" + id, {
            method: method,
            credentials: 'same-origin'
        }).then(function() {
            location.reload()
        });
    }
}

var deleteOffer = fetchAction('offers', 'DELETE');
var acceptOffer = fetchAction('offers', 'POST');
var deleteTrade = fetchAction('trades', 'DELETE');
var confirmTrade = fetchAction('trades', 'POST');

(function($) {
    var el = $('.captcha-image');
    el && el.addEventListener('click', refreshCaptcha);
    // var captchas = document.getElementsByClassName('captcha-image');
    // for (var i in captchas) {
    //     captchas[i].onclick = refreshCaptcha;
    // }
})(document.querySelector.bind(document));

