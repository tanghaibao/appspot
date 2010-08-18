function show_example(gid) {
    $('#gid').val(gid);
    submit();
};

function reset() {
    window.location = "/athaliana";
};

function submit() {
    var url = '/athaliana/query'
    var params = $('form').serialize();
    $('#response').html();

    window.location = url + "?" + params;
};

function page(p) {
    var url = '/athaliana/query'
    var params = $('form').serialize();
    params += '&page=' + p;
    $('#response').html();
    
    window.location = url + "?" + params;
}

$(function() {
    $("button, input[type=submit], input[type=reset]").button();
    $(".radio").buttonset();

    $("input#gid").autocomplete({
        source: "/athaliana/autocomplete"
    });
});
