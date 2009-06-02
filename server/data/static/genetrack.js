

function filter_rows(){
    // displays rows based on the content of the input
    var text = $("#filter-input").val().toLowerCase();
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
