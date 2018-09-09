$(document).ready(function() {
    $("tr.invoice-master").click(function(){
        $(this).children().eq(0).children().eq(0).toggleClass("caret-right-down");
        $(this).next().toggleClass("invoice-detail-active");
    });

    $("button.btn-invoices-expand").click(function() {
        $(this).parent().parent().find("tr.invoice-master").each(function() {
            $(this).children().eq(0).children().eq(0).addClass("caret-right-down");
            $(this).next().addClass("invoice-detail-active");
        });
    });

    $("button.btn-invoices-collapse").click(function() {
        $(this).parent().parent().find("tr.invoice-master").each(function() {
            $(this).children().eq(0).children().eq(0).removeClass("caret-right-down");
            $(this).next().removeClass("invoice-detail-active");
        });
    });
});

function generate_var_symbol(url, user_id, invoice_id, elem) {
    $.ajax({url: url, dataType: "json", success: function(result) {
        if ('var_symbol' in result) {
            $(elem).parent().text(result['var_symbol']);
        }
    }});
}
