$(document).ready(function() {
    $("tr.invoice-master").click(function(){
        $(this).next().toggle()
    });
});
