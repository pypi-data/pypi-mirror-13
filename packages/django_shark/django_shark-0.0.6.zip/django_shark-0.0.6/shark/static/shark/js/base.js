function send_action(post_data) {
    $.ajax({
        type: 'POST',
        url: window.location.href,
        data: post_data,
        dataType: 'json',

        success: function(data, status) {
            eval(data.javascript)
            bind_forms();
        }
    });
}

function do_action(action, post_data) {
    post_data.action = action;
    post_data.keep_variables = keep_variables;
    send_action(post_data);
}

function bind_forms() {
    // Send form data as AJAX
    $('form[data-async]').on('submit', function(event) {
        send_action($(this).serialize());

        event.preventDefault();
    });

    $('form[data-async]').each(function() {
        $('<input type="hidden" name="keep_variables">').attr('value', keep_variables).appendTo(this)
    })
}

$(document).ready(function() {
    // Autofocus the first element with data-autofocus on a modal
    $(".modal").on('shown.bs.modal', function() {
        $(this).find("[data-autofocus]:first").focus();
    });

    bind_forms();

    //TODO: Move
    $('.carousel').carousel()
});

//TODO: Move to themes.js
!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+"://platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");

