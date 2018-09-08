$(document).ready(function() {
    $("tr.invoice-master").click(function(){
        $(this).children().eq(0).children().eq(0).toggleClass("caret-right-down");
        $(this).next().toggleClass("invoice-detail-active");
    });
});
