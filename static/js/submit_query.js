/**
 * PROGRAM : query_submit
 * AUTHOR  : codeunsolved@gmail.com
 * CREATED : July 13 2017
 * VERSION : v0.0.1
 */

var dt = {};

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

$(document).ready(querySubmit());

function querySubmit() {
    $('#pending').click({'table': 'pending'}, queryDT);
    $('#approved').click({'table': 'approved'}, queryDT);
    $('#draft').click({'table': 'draft'}, queryDT);
    $('#accepted').click({'table': 'accepted'}, queryDT);

    $('#dt_pending').on('click', '.pending_action', popupAction);
    $('#dt_pending').on('click', '.pending_log', popupLog);
    $('#dt_draft').on('click', '.draft_delete', deleteDraft);

    $('#pending').trigger("click");
    $('#draft').trigger("click");

    function queryDT(event) {
        var table = event.data.table;
        var dt_id = 'dt_' + table;

        drawDataTable('#'+dt_id, dt_id, {
            "ajax": {
                "url": "/submit/query",
                "data": {
                    "tab": table,
                },
                "type": "post"
            },
            "drawCallback": function(settings) {
                var api = new $.fn.dataTable.Api( settings );
                var length = api.rows().data().length;
                //console.log("Data:"+length);
                if (table == 'pending') {
                    $('#'+table+'_num').text(length);
                } else if (table == 'draft') {
                    $('#'+table+'_num').text(length);
                }
            },
        });
    }

    function popupAction() {
        var submit_id = $(this).attr('submit_id');

        $.confirm({
            title: 'Approval submissionn',
            content: '' +
            '<form>' +
            '<div class="input-group">' +
            '<span class="input-group-addon">Action<span style="color:red;">*</span></span>' +
            '<select name="action" class="form-control">' +
            '<option value="" selected>- SELECT -</option>' +
            '<option value="Revision"> Revise </option>' +
            '<option value="Rejected"> Reject </option>' +
            '<option value="Accepted"> Accept </option>' +
            '</select>' +
            '</div>' +
            '<br>' +
            '<div class="input-group">' +
            '<span class="input-group-addon">Comments</span>' +
            '<textarea name="comments" class="form-control"></textarea>' +
            '</div>' +
            '</form>',
            buttons: {
                formSubmit: {
                    text: 'OK',
                    btnClass: 'btn-blue',
                    action: function () {
                        var action = this.$content.find('select[name=action]').val();
                        var comments = this.$content.find('textarea[name=comments]').val();
                        if(!action){
                            $.alert('Please select an action!');
                            return false;
                        } else {
                            $.post("/submit/add",
                                {'type': action,
                                 'submit_id': submit_id,
                                 'comments': comments},
                                function(data) {
                                    var alert_msg = '';
                                    if (data.code == 1) {
                                        alert_msg = 'Success!';
                                    } else if (data.code == 0) {
                                        alert_msg = 'Error!';
                                    }

                                    $.confirm({
                                        title: alert_msg,
                                        content: '',
                                        buttons: {
                                            ok: function () {
                                                window.location.reload();
                                            },
                                        },
                                    });
                                }
                            );
                        }
                    }
                },
                cancel: function () {
                    //close
                },
            },
        });
    }

    function popupLog() {
        var submit_id = $(this).attr('submit_id');

        $.post("/submit/add",
            {'type': 'Log',
             'submit_id': submit_id},
            function(data) {
                var table_data = data.data;
                var content = '<table class="table table-striped">' +
                              '<thead>' +
                              '<tr><th>Time</th><th>User</th><th>Action</th><th>Note</th></tr>' +
                              '</thead>' +
                              '<tbody>' +
                              '</tbody>' +
                              '</table>';
                var $content = $(content);

                for (var i = 0; i < table_data.length; i++) {
                    var row = '<tr>';
                    for (var j = 0; j < table_data[i].length; j++) {
                        row += '<td>';
                        row += table_data[i][j];
                        row += '</td>';
                    }
                    row += '</tr>';
                    $content.find('tbody').append(row);
                }
                $.confirm({
                    title: "Log",
                    content: $content.prop('outerHTML'),
                    buttons: {
                        ok: function () {
                            
                        },
                    },
                });
            }
        );
    }

    function deleteDraft() {
        var submit_id = $(this).attr('submit_id');
        $.confirm({
            title: '',
            content: 'Are you sure to delete?',
            buttons: {
                formSubmit: {
                    text: 'Yes',
                    btnClass: 'btn-blue',
                    action: function () {
                        var action = 'Delete';

                        $.post("/submit/add",
                            {'type': action,
                             'submit_id': submit_id},
                            function(data) {
                                var alert_msg = '';
                                if (data.code == 1) {
                                    alert_msg = 'Success!';
                                } else if (data.code == 0) {
                                    alert_msg = 'Error!';
                                }

                                $.confirm({
                                    title: alert_msg,
                                    content: '',
                                    buttons: {
                                        ok: function () {
                                            window.location.reload();
                                        },
                                    },
                                });
                            }
                        );
                    }
                },
                cancel: function () {
                    //close
                },
            },
        });
    }
}

// drawDataTable
function drawDataTable(id, fn, options_add) {
    var options = {
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
