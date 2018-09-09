$(document).ready(function() {
    $("tr.invoice-master").click(function(){
        $(this).children().eq(0).children().eq(0).toggleClass("caret-right-down");
        $(this).next().toggleClass("invoice-detail-active");
    });
});

function generate_var_symbol(url, id) {
    $.ajax({url: url, dataType: "json", success: function(result) {
        if ('var_symbol' in result) {
            $(".var-symbol-" + id).first().text(result['var_symbol']);
        }
    }});
}
