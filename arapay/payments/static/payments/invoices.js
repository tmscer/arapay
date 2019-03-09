$.ajaxSetup({
    beforeSend: function(xhr, settings) {
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
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

$(document).ready(function() {
    $("tr.row-master").click(function(){
        $(this).children().eq(0).children().eq(0).toggleClass("caret-right-down");
        $(this).next().toggleClass("row-detail-active");
    });

    $("button.btn-invoices-expand").click(function() {
        $(this).parent().parent().find("tr.row-master").each(function() {
            $(this).children().eq(0).children().eq(0).addClass("caret-right-down");
            $(this).next().addClass("row-detail-active");
        });
    });

    $("button.btn-invoices-collapse").click(function() {
        $(this).parent().parent().find("tr.row-master").each(function() {
            $(this).children().eq(0).children().eq(0).removeClass("caret-right-down");
            $(this).next().removeClass("row-detail-active");
        });
    });
});

function generate_var_symbol(url, user_id, invoice_id, elem) {
    $.ajax({
            url: url,
            type: "POST",
            dataType: "json",
            success: function(result) {
                var parent = $(elem).parent();
                parent.parent().parent().parent().parent()
                    .find(".qr-code").css("background-image", "url(" + result["url"] + ")");
                parent.text(result["var_symbol"]);
        }
    });
}

function change_payment_status(url, user_id, payment_id, elem) {
    $.ajax({
            url: url,
            type: "POST",
            dataType: "json",
            success: function(result) {
                var previousStatus = result['previous'];
                var status = result['status'];

                elem.innerHTML = status;
                $(elem).removeClass('payment-status-' + previousStatus.toLowerCase());
                $(elem).addClass('payment-status-' + status.toUpperCase());
        }
    });
}
