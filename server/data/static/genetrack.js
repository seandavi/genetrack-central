

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

    // assign the callback to filter input
    $("#filter-input").keyup( filter_rows ); 

    // searchbox gets focus
    $("#filter-input").focus()

    // highlits data rows on mouse hover
    $(".row").hover( function() {
        $(this).addClass("hover")
    }, function() {
        $(this).removeClass("hover")
    })
}

function remove_messages(){
    // removes messages after some time passes
    $("#messages")
        .animate({opacity: 1}, 3000)   // delay
        .animate({opacity: 0.0}, 1000) // fadeout
        .slideUp('slow', function() {  // remove
            $(this).remove();
        });
}