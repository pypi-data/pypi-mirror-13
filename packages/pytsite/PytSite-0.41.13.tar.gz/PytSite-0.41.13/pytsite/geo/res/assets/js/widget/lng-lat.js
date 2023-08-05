$(function () {
    $('.widget-geo-lng-lat').each(function () {
            var widget = $(this);
            var input = widget.find('input');

            if ('geolocation' in navigator && input.val() == '[0.0, 0.0]') {
                navigator.geolocation.getCurrentPosition(function (position) {
                    var coords = position.coords;
                    input.val(JSON.stringify([coords.longitude, coords.latitude])).change();
                });
            }
        }
    );
});
