/**
 * PROGRAM : submit_new
 * AUTHOR  : codeunsolved@gmail.com
 * CREATED : July 14 2017
 * VERSION : v0.0.1
 */

var content = {};

$(document).ready(addNew());

function addNew() {

    activeTab(step, 1);

    $('#STEP01_next').click(checkStep01);
    //$('#STEP02_next').click(checkStep02);
    //$('#STEP03_next').click(checkStep03);
    //$('#STEP04_next').click(checkStep04);
    //$('#STEP05_next').click(checkStep05);
    //$('#STEP06_next').click(checkStep06);
    //$('#STEP07_next').click(checkStep07);
    //$('#STEP08_next').click(checkStep08);

    function checkStep01() {
        var title = $("input[name='title_']").val();
        var pubmed_id = $("input[name='pubmed_id_']").val();

        if (checkForm(1)) {
            if (!(pubmed_id.length == 0 || pubmed_id.match(/^\s+$/g))) {
                content['step01'] = {'title': title, 'pubmed_id': pubmed_id};
            } else {
                content['step01'] = {'title': title};
            }

            querySubmit({
                'kb': 'SNP',
                'step': 1,
                'content' : JSON.stringify(content)
            }, 1);
        }
    }
}

function activeTab(id, loop) {
    if (loop == 0) {
        $("#STEP0"+id.toString()+"_nav").parent().removeClass("disabled");
        $("#STEP0"+id.toString()+"_nav").attr("data-toggle", "tab");
    } else {
        for (var i = 2; i <= id; i++) {
            $("#STEP0"+i.toString()+"_nav").parent().removeClass("disabled");
            $("#STEP0"+i.toString()+"_nav").attr("data-toggle", "tab");
        }
    }
}

function checkForm(id) {
    var valid = true;

    $("#STEP0"+id.toString()+"_form input:required").each(function() {
        var v = $(this).val();
        if (v.length == 0 || v.match(/^\s+$/g)) {
            $("#STEP0"+id.toString()+"_msg").html(formatErrorMsg('Got empty required field(s)'));
            valid = false;
            return false;
        }
    });
    return valid;
}

function formatErrorMsg(msg) {
    var error_msg = '<div class="alert alert-danger alert-dismissible fade in">' +
                    '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                    '<span aria-hidden="true">×</span></button><strong>' + msg + '</strong></div>';
    return error_msg
}

function querySubmit(data, id) {
    $.post("/submit/add",
        data,
        function(data) {
            if (data.code == 1) {
                if (id < 8) {
                    activeTab(id+1, 0);
                    $("#STEP0"+(id+1).toString()+"_nav").trigger("click");
                } else if (id == 8) {

                }
            } else if (data.code == 0) {
                $("#STEP0"+id.toString()+"_msg").html(formatErrorMsg(data.msg));
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
