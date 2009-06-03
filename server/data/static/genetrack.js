

function filter_rows(){
    // displays rows based on the content of the input
    var text = $("#filter-input").val().toLowerCase();
    text = jQuery.trim(text)
    if (text.length == 0) {
        $(".row").show();
        $('#filter-box').removeClass("notice")
        $('#filter-info').html('')

    } else {
        $(".row").hide();
        $('#filter-box').addClass("notice")
        $('#filter-info').html('&bull; <span class="filter info">filtered with "' + text + '"</span>')
        $(".row:contains('" + text +"')").show()
    }
}

function remove_messages(){
    // removes messages after a 3 seconds
    $("#messages")
        .animate({opacity: 1}, 2000)
        .animate({opacity: 0.0}, 1000)
        .slideUp('slow', function() {
            $(this).remove();
        });
}