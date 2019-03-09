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
            type: "PUT",
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
