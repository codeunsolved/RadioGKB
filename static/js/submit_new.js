/**
 * PROGRAM : submit_new
 * AUTHOR  : codeunsolved@gmail.com
 * CREATED : July 14 2017
 * VERSION : v0.0.1
 */

$(document).ready(addNew());

function addNew() {
    var step_now = 1;
    var tumor_num = 1;
    var prognosis_num = 1;

    activeTab(step, true);

    $('#STEP01_nav').click({'id': 1}, setStep);
    $('#STEP02_nav').click({'id': 2}, setStep);
    $('#STEP03_nav').click({'id': 3}, setStep);
    $('#STEP04_nav').click({'id': 4}, setStep);
    $('#STEP05_nav').click({'id': 5}, setStep);
    $('#STEP06_nav').click({'id': 6}, setStep);
    $('#STEP07_nav').click({'id': 7}, setStep);

    $('.next').click({'type': 'next'}, checkStep);
    $('.save').click({'type': 'save'}, checkStep);
    $('.back').click(backStep);

    $('#STEP03_tumor_add').click(addTumor);
    $('#STEP04_nav').click(genStep04);
    $('#STEP04_form').on('click', '.STEP04_variant_add', addTumorGene); //DOM changed, click() doesn't work
    $('#STEP05_prognosis_add').click(addPrognosis);

    function setStep(event) {
        step_now = event.data.id;
        console.log("STEP:0"+step_now);
    }

    function checkStep(event) {
        var id = step_now;
        var type = event.data.type;
        var step_id = 'STEP0' + id.toString();
        var form = {};

        content[step_id] = {};

        $("#"+step_id+"_form :input").each(function() {
            var key = $(this).attr("name");
            form[key] = $(this).val();
            //console.log(key);
            //console.log(form[key]);
        });

        if (checkForm(step_id)) {
            if (id == 1) {
                if (!(form.pubmed_id_.length == 0 || form.pubmed_id_.match(/^\s+$/g))) {
                    content[step_id] = {'title': form.title_, 'pubmed_id': form.pubmed_id_};
                } else {
                    content[step_id] = {'title': form.title_};
                }
            } else if (id == 3) {
                content[step_id]['tumor'] = [];
                $("#"+step_id+"_form .tumor").each(function() {
                    var tumor_vals = {};
                    $(":input", this).each(function() {
                        var key = $(this).attr("name");
                        tumor_vals[key] = $(this).val();
                    });
                    content[step_id]['tumor'].push(tumor_vals);
                });
            } else {
                for (var key in form) {
                     content[step_id][key] = form[key];
                }
            }

            querySubmit({
                'kb': 'SNP',
                'step': id,
                'content' : JSON.stringify(content)
            }, id, type);
        }
    }

    function backStep() {
        $("#STEP0"+(step_now-1).toString()+"_nav").trigger("click");
    }

    function activeTab(id, loop) {
        if (loop) {
            for (var i = 2; i <= id; i++) {
                $("#STEP0"+i.toString()+"_nav").parent().removeClass("disabled");
                $("#STEP0"+i.toString()+"_nav").attr("data-toggle", "tab");
            }
        } else {
            $("#STEP0"+id.toString()+"_nav").parent().removeClass("disabled");
            $("#STEP0"+id.toString()+"_nav").attr("data-toggle", "tab");
        }
    }

    function checkForm(step_id) {
        var valid = true;

        $("#"+step_id+"_form").find("input:required, select").each(function() {
            var v = $(this).val();
            if (v.length == 0 || v.match(/^\s+$/g)) {
                $("#"+step_id+"_msg").html(formatMsg('Got empty required field(s)', 'danger'));
                valid = false;
                return false;
            }
        });
        return valid;
    }

    function querySubmit(data, id, type) {
        $.post("/submit/add",
            data,
            function(data) {
                if (data.code == 1) {
                    if (type == 'save') {
                        $("#STEP0"+id.toString()+"_msg").html(formatMsg('Save successful!', 'success'));
                    } else if (type == 'next') {
                        if (id < 8) {
                            activeTab(id+1, false);
                            $("#STEP0"+(id+1).toString()+"_nav").trigger("click");
                        }

                        if (id == 1) {
                            if ('pubmed_id' in content.STEP01) {
                                $("input[name='pubmed_id']").val(content.STEP01.pubmed_id);
                                $("input[name='pubmed_id']").prop('disabled', true);
                            } else {
                                $("input[name='pubmed_id']").val('');
                                $("input[name='pubmed_id']").removeAttr("disabled");
                            }
                            $("input[name='title']").val(content.STEP01.title);
                            $("input[name='title']").prop('disabled', true);
                        }
                    }
                } else if (data.code == 0) {
                    $("#STEP0"+id.toString()+"_msg").html(formatMsg(data.msg, 'danger'));
                }
            }
        );
    }

    function formatMsg(msg, type) {
        var msg_html = '<div class="alert alert-' + type + ' typedanger alert-dismissible fade in">' +
                       '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                       '<span aria-hidden="true">×</span></button><strong>' + msg + '</strong></div>';
        return msg_html
    }

    function addTumor() {
        tumor_num += 1;
        tumor_html = '<div id="tumor_' + tumor_num + '" class="panel panel-success"><div class="panel-heading">' +
                     '<strong>Tumor No.' + tumor_num.toString() + '</strong>' +
                     '<span class="pull-right glyphicon glyphicon-minus" onclick="$(\'#tumor_' + tumor_num +
                     '\').remove();" style="cursor:pointer;color:red;"></span>' +
                     '</div><div class="panel-body tumor"><div class="input-group">' +
                     '<span class="input-group-addon">Tumor Ontology Name' +
                     '<span style="color:red;">*</span></span><input name="tumor"' +
                     ' class="form-control" type="text" required>' +
                     '</div><br><div class="input-group"><span class="input-group-addon">' +
                     'MeSH term</span><input name="mesh_term" class="form-control" ' +
                     'type="text"></div><br><div class="input-group">' +
                     '<span class="input-group-addon">MeSH id</span>' +
                     '<input name="mesh_id" class="form-control" type="number">' +
                     '</div></div></div>';
        $('#tumor_above').before(tumor_html);
    }

    function genStep04() {
        var tumor_gene_html = '';
        tumors = content.STEP03.tumor;

        for (var i = 0; i < tumors.length; i++) {
            tumor_gene_html += '<div class="panel panel-success"><div class="panel-heading">' +
                               '<strong>Tumor: ' + tumors[i].tumor + '</strong></div>' +
                               '<div class="panel-body tumor_gene"><div class="panel panel-default">' +
                               '<div class="panel-body gene_variant"><div class="input-group">' +
                               '<span class="input-group-addon">Gene Symbol<span style="color:red;">*</span></span>' +
                               '<input name="gene" class="form-control" type="text" required></div><br>' +
                               '<div class="input-group"><span class="input-group-addon">Entrez Gene ID</span>' +
                               '<input name="entrez_id" class="form-control" type="number"></div><br>' +
                               '<div class="input-group"><span class="input-group-addon">dbSNP RS ID' +
                               '<span style="color:red;">*</span></span><input name="dbsnp" ' +
                               'class="form-control" type="text" required></div></div></div>' +
                               '<div class="variant_above"></div><div><span ' +
                               ' class="btn glyphicon glyphicon-plus-sign STEP04_variant_add" ' +
                               'style="cursor:pointer;font-size:1.5em;color:limegreen;">' +
                               '</span></div></div></div>';
        }
        $('#STEP04_container').html(tumor_gene_html);
    }

    function addTumorGene() {
        gene_variant_html = '<div class="panel panel-default"><div class="panel-body gene_variant">' +
                            '<div class="input-group"><span class="input-group-addon">' +
                            'Gene Symbol<span style="color:red;">*</span></span>' +
                            '<input name="gene" class="form-control" type="text" required>' +
                            '</div><br><div class="input-group"><span class="input-group-addon">' +
                            'Entrez Gene ID</span><input name="entrez_id" class="form-control" ' +
                            'type="number"></div><br><div class="input-group">' +
                            '<span class="input-group-addon">dbSNP RS ID<span style="color:red;">' +
                            '*</span></span><input name="dbsnp" class="form-control" type="text" required>' +
                            '</div></div></div>';
        $(this).parent().parent().find('.variant_above').before(gene_variant_html);
    }

    function addPrognosis () {
        
    }
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
