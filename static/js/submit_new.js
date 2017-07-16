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

    var tumor_html = $('#STEP03_form .panel').prop('outerHTML');
    var variant_html = $('#STEP04_form .variant').parent().prop('outerHTML');
    var tumor_variant_html = $('#STEP04_container').html();
    var prognosis_html = $('#STEP05_form .panel').prop('outerHTML');

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
    $('#STEP03_form').on('click', '.STEP03_tumor_minus', minusTumor); //DOM changed, click() doesn't work
    $('#STEP04_nav').click(genStep04);
    $('#STEP04_form').on('click', '.STEP04_variant_add', addVariant);
    $('#STEP04_form').on('click', '.STEP04_variant_minus', minusVariant);
    $('#STEP04_form').on('click', '.STEP04_gene_new', toggleGeneNew);
    $('#STEP04_form').on('click', '.STEP04_gene_existed', toggleGeneExisted);
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

        content[step_id] = {}; // reset

        $("#"+step_id+"_form :input").each(function() {
            var key = $(this).attr("name");
            form[key] = $(this).val();
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
            } else if (id == 4) {
                content[step_id]['variant'] = [];
                $("#"+step_id+"_form .tumor_variant").each(function() {
                    var variants = [];
                    $(".variant", this).each(function() {
                        var new_ = false;
                        var gene = $(this).find('input[name=gene]').val();
                        if ($(this).find('.STEP04_gene_new').is(":checked")) {
                            gene = $(this).find('input[name=gene_new]').val();
                            new_ = true;
                        }
                        var entrez_id = $(this).find('input[name=entrez_id]').val();
                        var dbsnp = $(this).find('input[name=dbsnp]').val();
                        variants.push({'gene': gene, 'new': new_, 'entrez_id': entrez_id, 'dbsnp': dbsnp});
                    });
                    content[step_id]['variant'].push(variants);
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
        var msgs = [];

        $("#"+step_id+"_form").find("input:required, select").each(function() {
            var v = $(this).val();
            if (v.length == 0 || v.match(/^\s+$/g)) {
                msgs.push('Please fill required field(s)');
                valid = false;
                return false;
            }
        });
        if (step_id == 'STEP04') {
            $("#"+step_id+"_form").find("input[name=gene]:required").each(function() {
                var v = $(this).val();
                if ($.inArray(v, genes) == -1) {
                    console.log(v);
                    msgs.push('Please use Gene Symbol in suggestions! If it is not in suggestions, please specify a new one.');
                    valid = false;
                    return false;
                }
            });
        }
        if (msgs.length >= 1) {
            $("#"+step_id+"_msg").html(formatMsg(msgs.join('<br><br>'), 'danger'));
        }
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
        return msg_html;
    }

    function addTumor() {
        var tumor_minus_html = '<span class="pull-right glyphicon glyphicon-minus STEP03_tumor_minus" style="cursor:pointer;color:red;"></span>';
        var $tumor_html = $(tumor_html);
        tumor_num += 1;

        $tumor_html.find('#STEP03_tumor_no').text("Tumor No."+tumor_num.toString());
        $tumor_html.find('#STEP03_tumor_no').after(tumor_minus_html);
        $tumor_html.insertBefore('#tumor_above');
    }

    function minusTumor() {
        $(this).parent().parent().remove();
    }

    function genStep04() {
        if ('STEP03' in content) {
            var tumors = content.STEP03.tumor;
            var tumor_variant_htmls = '';
            for (var i = 0; i < tumors.length; i++) {
                var $tumor_variant_html = $(tumor_variant_html);
                $tumor_variant_html.find('#STEP04_tumor_name').text("Tumor: "+tumors[i].tumor);
                tumor_variant_htmls += $tumor_variant_html.prop('outerHTML');
            }
            $('#STEP04_container').html(tumor_variant_htmls);
        } else {
            $('#STEP04_container').html('');
            $("#STEP04_msg").html(formatMsg('Please complete STEP03 Tumor first!', 'danger'));
        }
    }

    function addVariant() {
        var variant_minus_html = '<div class="col-md-12 col-sm-12 col-xs-12">' +
                                 '<span class="pull-right glyphicon glyphicon-minus STEP04_variant_minus" ' +
                                 'style="cursor:pointer;color:red;"></span><br></div>';
        var $variant_html = $(variant_html);
        $variant_html.find('.STEP04_gene_existed').before(variant_minus_html);
        $(this).parent().parent().find('.variant_above').before($variant_html.prop('outerHTML'));
    }

    function minusVariant() {
        $(this).parent().parent().parent().remove();
    }

    function toggleGeneNew() {
        var gene_existed = $(this).parent().parent().parent().find('input[name=gene]');
        var gene_new = $(this).parent().parent().find('input[name=gene_new]');
        gene_existed.prop('disabled', true);
        gene_existed.prop('required', false);
        gene_new.prop('disabled', false);
        gene_new.prop('required', true);
    }

    function toggleGeneExisted() {
        var gene_existed = $(this).find('input[name=gene]');
        var gene_new = $(this).parent().parent().find('input[name=gene_new]');
        gene_existed.prop('disabled', false);
        gene_existed.prop('required', true);
        gene_new.prop('disabled', true);
        gene_new.prop('required', false);
        $(this).parent().find('.STEP04_gene_new').prop('checked', false);
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
