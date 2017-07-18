/**
 * PROGRAM : query_submit
 * AUTHOR  : codeunsolved@gmail.com
 * CREATED : July 13 2017
 * VERSION : v0.0.1
 */

var dt = {};

$(document).ready(querySubmit());

function querySubmit() {
    $('#pending').click(queryPending);
    $('#approved').click(queryApproved);
    $('#draft').click(queryDraft);
    $('#accepted').click(queryAccepted);

    $('#pending').trigger("click");
    $('#draft').trigger("click");
}

// drawDataTable
function drawDataTable(id, fn, options_add) {
    var options = {
        "dom": "lfrtip",
        "responsive": true
    };

    for (var key in options_add) { options[key] = options_add[key]; }

    if ($.fn.dataTable.isDataTable(id)) {
        dt[id].destroy();
    }
    dt[id] = $(id).DataTable(options);
}

// CSRF
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});
