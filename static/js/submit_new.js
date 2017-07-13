/**
 * PROGRAM : submit_new
 * AUTHOR  : codeunsolved@gmail.com
 * CREATED : July 14 2017
 * VERSION : v0.0.1
 */

$(document).ready(addNew());

function addNew() {
    $('#STEP01_next').click(checkStep01);
    $('#STEP02_next').click(checkStep02);
    $('#STEP03_next').click(checkStep03);
    $('#STEP04_next').click(checkStep04);
    $('#STEP05_next').click(checkStep05);
    $('#STEP06_next').click(checkStep06);
    $('#STEP07_next').click(checkStep07);
    $('#STEP08_next').click(checkStep08);

    function checkStep01() {
        var title = $("input[name='title']").val();
        var pubmed_id = $("input[name='pubmed_id']").val();

        if (!(pubmed_id.length == 0 || pubmed_id.match(/^\s+$/g))) {
            querySubmit({
                'step': 1,
                'content' : {'step01': {'title': title, 'pubmed_id': pubmed_id}}
            }, 1);
        }
    }
}

function querySubmit(data, id) {
    $.post("/query_submit",
        data,
        function(data) {
            if (data.code == 1) {
                if (id < 8) {
                    $("#STEP0"+(id+1).toString()+"_nav").removeClass("disable");
                    $("#STEP0"+(id+1).toString()+"_nav").attr("data-toggle", "tab");
                    $("#STEP0"+(id+1).toString()+"_nav").trigger("click");
                } else if (id == 8) {

                }
            } else if (data.code == 0) {
                $("#STEP0"+id.toString()+"_msg").html(
                    '<div class="alert alert-danger alert-dismissible fade in">' +
                    '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                    '<span aria-hidden="true">×</span></button><strong>' + data.msg +
                    '</strong></div>'
                );
            }
        }
    );
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
