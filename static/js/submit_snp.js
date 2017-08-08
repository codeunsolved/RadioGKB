/**
 * PROGRAM : submit_snp
 * AUTHOR  : codeunsolved@gmail.com
 * CREATED : July 14 2017
 * VERSION : v0.0.1
 */

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

$(document).ready(addNew());

function addNew() {
    var step_now = content.step_now;
    var step_max = content.step_max;
    var tumor_num = 1;
    var prognosis_num = 1;
    var association_num = 1;
    var recur_step04 = 0;
    var recur_step06 = 0;

    var tumor_html = $('#STEP03_form .panel').first().prop('outerHTML');
    var variant_html = $('#STEP04_form .STEP04_variant').first().parent().prop('outerHTML');
    var tumor_variant_html = $('#STEP04_form .panel').first().prop('outerHTML');
    var prognosis_html = $('#STEP05_form .panel').first().prop('outerHTML');
    var association_html = $('#STEP06_form .panel').first().prop('outerHTML'); //reassigned in genStep06()
    var association_row_html = $('.STEP06_row').first().prop('outerHTML');
    var step06_container_html = $('#STEP06_container').html();

    activeTab(step_max, true);

    $('#STEP01_nav').click({'id': 1}, setStep);
    $('#STEP02_nav').click({'id': 2}, setStep);
    $('#STEP03_nav').click({'id': 3}, setStep);
    $('#STEP04_nav').click({'id': 4}, setStep);
    $('#STEP05_nav').click({'id': 5}, setStep);
    $('#STEP06_nav').click({'id': 6}, setStep);
    $('#STEP07_nav').click({'id': 7}, setStep);

    $('.next').click({'action': 'next'}, checkStep);
    $('.save').click({'action': 'save'}, checkStep);
    $('.back').click(backStep);

    uploadPaper();
    $('#STEP03_tumor_add').click(addTumor);
    $('#STEP03_form').on('click', '.STEP03_tumor_minus', minusTumor); //DOM changed, click() doesn't work
    $('#STEP04_form').on('click', '.STEP04_variant_add', addVariant);
    $('#STEP04_form').on('click', '.STEP04_variant_minus', minusVariant);
    $('#STEP04_form').on('click', '.STEP04_gene_new', toggleGeneNew);
    $('#STEP04_form').on('click', '.STEP04_gene_existed', toggleGeneExisted);
    $('#STEP05_prognosis_add').click(addPrognosis);
    $('#STEP05_form').on('click', '.STEP05_prognosis_minus', minusPrognosis);
    $('#STEP05_form').on('click', '.STEP05_subgroup_add', addSubgroup);
    $('#STEP05_form').on('click', '.STEP05_subgroup_minus', minusSubgroup);
    $('#STEP06_association_add').click(addAssociation);
    $('#STEP06_form').on('click', '.STEP06_association_minus', minusAssociation);
    //$('#STEP06_form').on('click', '.STEP06_column_add', addAssociationColumn);
    //$('#STEP06_form').on('click', '.STEP06_column_minus', minusAssociationColumn);
    $('#STEP06_form').on('click', '.STEP06_row_add', addAssociationRow);
    $('#STEP06_form').on('click', '.STEP06_row_minus', minusAssociationRow);
    $('#STEP06_form').on('change', '.STEP06_tumor', changeGene);
    $('#STEP06_form').on('change', '.STEP06_gene', changeVariant);
    $('#STEP06_form').on('change', '.STEP06_prognosis', changeSubgroup);
    $('#STEP07_submit').click(submit);

    if (review_mode) {
        reviewSubmit();
    }

    function setStep(event) {
        step_now = event.data.id;
        console.log("NOW:STEP0"+step_now);
    }

    function checkStep(event) {
        var id = step_now;
        var action = event.data.action;
        var step_id = 'STEP0' + id.toString();

        content.step_now = id;
        content[step_id] = {}; // reset

        if (checkForm(step_id)) {
            if (id == 3) {
                content[step_id]['tumor'] = [];
                $("#"+step_id+"_form .STEP03_tumor").each(function() {
                    var tumor_vals = {};
                    $(":input", this).each(function() {
                        var name = $(this).attr("name");
                        tumor_vals[name] = $(this).val();
                    });
                    content[step_id]['tumor'].push(tumor_vals);
                });
            } else if (id == 4) {
                content[step_id]['variant'] = [];
                $("#"+step_id+"_form .STEP04_tumor").each(function() {
                    var variants = [];
                    $(this).find('.STEP04_variant').each(function() {
                        var form = {'new': false};
                        $(":input", this).each(function() {
                            var name = $(this).attr("name");
                            form[name] = $(this).val();
                        });
                        if ($(this).find('.STEP04_gene_new').is(":checked")) {
                            form.new = true;
                        }
                        variants.push(form);
                    });
                    content[step_id]['variant'].push(variants);
                });
            } else if (id == 5) {
                content[step_id]['prognosis'] = [];
                $("#"+step_id+"_form .STEP05_prognosis").each(function() {
                    var form = {};
                    var subgroup = [];
                    $(":input", this).each(function() {
                        var name = $(this).attr("name");
                        if (name != 'subgroup') {
                            form[name] = $(this).val();
                        } else {
                            subgroup.push($(this).val());
                        }
                    });
                    form['subgroup'] = subgroup;
                    content[step_id]['prognosis'].push(form);
                });
            } else if (id ==6) {
                content[step_id]['association'] = [];

                $("#"+step_id+"_form .STEP06_association").each(function() {
                    var form = [];

                    var form_meta = {};
                    $(".STEP06_association_meta :input", this).each(function() {
                        var name = $(this).attr("name");
                        form_meta[name] = $(this).val();
                    });

                    $(".STEP06_association_genotype tbody tr", this).each(function() {
                        var form_genotype = {};
                        $(":input", this).each(function() {
                            var name = $(this).attr("name");
                            form_genotype[name] = $(this).val();
                        });
                        form.push(Object.assign(form_genotype, form_meta)); //merge two hash
                    });

                    content[step_id]['association'].push(form);
                });
            } else {
                $("#"+step_id+"_form :input").each(function() {
                    var name = $(this).attr("name");
                    content[step_id][name] = $(this).val();
                });
            }

            querySubmit({
                'kb': 'SNP',
                'action': action,
                'content' : JSON.stringify(content)
            }, id, action);
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

    function freezePubmedId() {
        $("#STEP02_form input[name='pubmed_id']").val(content.STEP01.pubmed_id);
        $("#STEP02_form input[name='pubmed_id']").prop('disabled', true);
    }

    function querySubmit(data, id, action) {
        $.post("/submit/add",
            data,
            function(data) {
                if (data.code == 1) {
                    if (action == 'save') {
                        $("#STEP0"+id.toString()+"_msg").html(formatMsg('Save successful!', 'success'));
                    } else if (action == 'next') {
                        if (id < 7) {
                            activeTab(id+1, false);
                            $("#STEP0"+(id+1).toString()+"_nav").trigger("click");
                        }

                        if (id == 1) {
                            //redirect to avoid restart a new submit by refresh
                            window.location.replace("/snp/add/"+data.submit_id.toString());
                        } else if (id == 3) {
                            genStep04();
                        } else if (id == 5) {
                            genStep06();
                        }
                    } else if (action == 'submit') {
                        $.confirm({
                            title: ' ',
                            content: 'Submit successfully!',
                            buttons: {
                                ok: function () {
                                    window.location.replace("/profile#submit");
                                },
                            },
                            theme: 'bootstrap',
                        });
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

    function uploadPaper() {
        $('#STEP02_paper_upload').fileupload({
            url: '/submit/add',
            dataType: 'json',
            formData: {action: 'upload', submit_id: content['submit_id']},
            submit: function (e, data) {
                var error = false;

                $('#STEP02_upload_progress .progress-bar').attr('class', "progress-bar progress-bar-warning");
                $('#STEP02_upload_progress .progress-bar').css('width', '0%');
                $('#STEP02_paper_table').css('opacity', 1);
                $.each(data.files, function (index, file) {
                    var paper_name = content.STEP01.pubmed_id.toString() + '_' + file.name;
                    var paper_size = (file.size/1000/1000).toFixed(3);
                    var error_msg = [];

                    $('#STEP02_paper_filename').text(paper_name);
                    $('#STEP02_paper_size').text(paper_size.toString()+" MB");

                    if (paper_size >= 20) {
                        error_msg.push("Uploading paper exceeds the maximum upload size: 20MB");
                        error = true;
                    }
                    if (paper_name.search(/\.(pdf|zip)$/i) == -1) {
                        error_msg.push("Uploading paper only accepts pdf/zip format");
                        error = true;
                    }

                    if (error_msg.length > 0) {
                        $("#STEP02_msg").html(formatMsg(error_msg.join('<br>'), 'danger'));
                    }
                });

                if (error) {
                    return false;
                }
            },
            done: function (e, data) {
                if (data.result.error) {
                    $('#STEP02_upload_progress .progress-bar').attr('class', "progress-bar progress-bar-danger");
                    $("#STEP02_msg").html(formatMsg(data.result.error, 'danger'));
                } else {
                    $.each(data.files, function (index, file) {
                        var paper_name = file.name;
                        var paper_size = (file.size/1000/1000).toFixed(3);
                        var paper_link = data.result.url

                        $('#STEP02_upload_progress .progress-bar').attr('class', "progress-bar progress-bar-success");
                        $('#STEP02_paper_download').show();
                        $('#STEP02_paper_download').attr('href', paper_link);
                    });
                }
            },
            progressall: function (e, data) {
                var progress = parseInt(data.loaded / data.total * 100, 10);
                $('#STEP02_upload_progress .progress-bar').css('width', progress + '%');
            },
        });
    }

    function addTumor() {
        var tumor_minus_html = '<span class="pull-right glyphicon glyphicon-minus STEP03_tumor_minus" style="cursor:pointer;color:red;"></span>';
        var $tumor_html = $(tumor_html);
        tumor_num += 1;

        $tumor_html.find('#STEP03_tumor_no').text("Tumor No."+tumor_num.toString());
        $tumor_html.find('#STEP03_tumor_no').after(tumor_minus_html);
        $tumor_html.insertBefore('#tumor_above');
        recur_step04 = 1;
    }

    function minusTumor() {
        $(this).parent().parent().remove();
        recur_step04 = 1;
    }

    function genStep04() {
        function genFrame() {
            var tumors = content.STEP03.tumor;
            var tumor_variant_htmls = '';

            for (var i = 0; i < tumors.length; i++) {
                var $tumor_variant_html = $(tumor_variant_html);
                $tumor_variant_html.find('#STEP04_tumor_name').text("Tumor: "+tumors[i].tumor);
                tumor_variant_htmls += $tumor_variant_html.prop('outerHTML');
            }
            $('#STEP04_container').html(tumor_variant_htmls);
        }
        if ('STEP04' in content) {
            if (recur_step04) {
                genFrame();
                recur_step04 = 0;
            } else {}
        } else if ('STEP03' in content) {
            genFrame();
        } else {
            $('#STEP04_container').html('');
            $("#STEP04_msg").html(formatMsg('Please complete STEP03: Tumor first!', 'danger'));
        }
    }

    function addVariant() {
        var variant_minus_html = '<div class="col-md-12 col-sm-12 col-xs-12"><span class="pull-right glyphicon glyphicon-minus STEP04_variant_minus" style="cursor:pointer;color:red;"></span><br></div>';
        var $variant_html = $(variant_html);

        $variant_html.find('.STEP04_gene_existed').before(variant_minus_html);
        $(this).parent().parent().find('.variant_above').before($variant_html.prop('outerHTML'));
        recur_step04 = 1;
    }

    function minusVariant() {
        $(this).parent().parent().parent().remove();
        recur_step04 = 1;
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
        var prognosis_minus_html = '<span class="pull-right glyphicon glyphicon-minus STEP05_prognosis_minus" style="cursor:pointer;color:red;"></span>';
        var $prognosis_html = $(prognosis_html);
        prognosis_num += 1;

        $prognosis_html.find('#STEP05_prognosis_no').text("Prognosis No."+prognosis_num.toString());
        $prognosis_html.find('#STEP05_prognosis_no').after(prognosis_minus_html);
        $prognosis_html.insertBefore('#prognosis_above');
        recur_step06 = 1;
    }

    function minusPrognosis () {
        $(this).parent().parent().remove();
        recur_step06 = 1;
    }

    function addSubgroup() {
        var subgroup_html = '<div class="input-group">' +
                            '<input name="subgroup" class="form-control" type="text" style="border-radius:0px;border-top-width:0px;">' +
                            '<span class="input-group-addon STEP05_subgroup_minus" style="cursor:pointer;width:35px;"><strong style="color:red;">-</strong></span>' +
                            '</div>';

        $(this).parent().parent().find('.subgroup_above').before(subgroup_html);
        recur_step06 = 1;
    }

    function minusSubgroup() {
        $(this).parent().remove();
        recur_step06 = 1;
    }

    function genStep06() {
        function genFrame() {
            var tumors = content.STEP03.tumor;
            var prognoses = content.STEP05.prognosis;
            var tumors_options_html = '<option value="" selected>- SELECT -</option>';
            var prognoses_options_html = '<option value="" selected>- SELECT -</option>';

            for (var i = 0; i < tumors.length; i++) {
                tumors_options_html += '<option value="'+tumors[i].tumor+'" index_tumor="'+i.toString()+'">'+tumors[i].tumor+'</option>';
            }
            for (var i = 0; i < prognoses.length; i++) {
                prognoses_options_html += '<option value="'+prognoses[i].prognosis_name+'" index_prognosis="'+i.toString()+'">'+prognoses[i].prognosis_name+'</option>';
            }

            $('#STEP06_container').html(step06_container_html);
            $('#STEP06_form .panel').first().find('.STEP06_tumor').html(tumors_options_html);
            $('#STEP06_form .panel').first().find('.STEP06_prognosis').html(prognoses_options_html);
            association_html = $('#STEP06_form .panel').first().prop('outerHTML');
        }
        var missing_steps = [];

        if (!('STEP03' in content)) {
            missing_steps.push('STEP03: Tumor')
        }
        if (!('STEP04' in content)) {
            missing_steps.push('STEP04: Gene & Variant')
        }
        if (!('STEP05' in content)) {
            missing_steps.push('STEP05: Prognosis')
        }

        if (missing_steps.length >= 1) {
            $('#STEP06_container').html('');
            $("#STEP06_msg").html(formatMsg('Please complete '+missing_steps.join(', ')+' first!', 'danger'));
        } else if ('STEP06' in content) {
            if (recur_step06) {
                genFrame();
                recur_step06 = 0;
            } else {}
        } else {
            genFrame();
        }
    }

    function changeGene() {
        if ($(this).val != "") {
            var i_tumor = parseInt($(":selected", this).attr('index_tumor'));
            var genes_options_html = '<option value="" selected>- SELECT -</option>';
            var genes = [];
            var genes_index = {}; //for deduplication and storing variant's first index(no need all of them)

            var variants = content.STEP04.variant[i_tumor];
            for (var i = 0; i < variants.length; i++) {
                var gene = '';
                if (variants[i].new) {
                    gene = variants[i].gene_new;
                } else {
                    gene = variants[i].gene;
                }
                if (!genes_index.hasOwnProperty(gene)) {
                    genes_index[gene] = i;
                    genes.push(gene);
                }
            }

            for (var i = 0; i < genes.length; i++) {
                genes_options_html += '<option value="'+genes[i]+'" index_tumor="'+i_tumor.toString()+'">'+genes[i]+'</option>';
            }

            $(this).parent().parent().parent().find('.STEP06_gene').html(genes_options_html);
        }
    }

    function changeVariant() {
        if ($(this).val != "") {
            var i_tumor = parseInt($(":selected", this).attr('index_tumor'));
            var gene = $(this).val();
            var variants_options_html = '<option value="" selected>- SELECT -</option>';

            var variants = content.STEP04.variant[i_tumor];
            var dbsnps = []; // maybe duplicate actually

            for (var i = 0; i < variants.length; i++) {
                var gene_ = '';
                if (variants[i].new) {
                    gene_ = variants[i].gene_new;
                } else {
                    gene_ = variants[i].gene;
                }

                if (gene == gene_) {
                    dbsnps.push(variants[i].dbsnp);
                }
            }

            for (var i = 0; i < dbsnps.length; i++) {
                variants_options_html += '<option value="'+dbsnps[i]+'">'+dbsnps[i]+'</option>';
            }

            $(this).parent().parent().parent().find('.STEP06_variant').html(variants_options_html);
        }
    }

    function changeSubgroup() {
        if ($(this).val != "") {
            var i_prognosis = parseInt($(":selected", this).attr('index_prognosis'));
            var subgroup_options_html = '<option value="" selected>- SELECT -</option>';

            var subgroups = [];
            var subgroups_ = content.STEP05.prognosis[i_prognosis].subgroup;
            var $subgroup = $(this).parent().parent().parent().find('.STEP06_subgroup');

            // filter empty value
            for (var i = 0; i < subgroups_.length; i++) {
                if (subgroups_[i] != "") {
                    subgroups.push(subgroups_[i]);
                }
            }

            if (subgroups.length == 0) {
                subgroup_options_html = '<option value="- N/A -" selected>- N/A -</option>';
                $subgroup.html(subgroup_options_html);
                $subgroup.prop('disabled', true);
            } else {
                for (var i = 0; i < subgroups.length; i++) {
                    subgroup_options_html += '<option value="'+subgroups[i]+'">'+subgroups[i]+'</option>';
                }
                $subgroup.html(subgroup_options_html);
                $subgroup.removeAttr("disabled");
            }
        }
    }

    function addAssociation() {
        var association_minus_html = '<span class="pull-right glyphicon glyphicon-minus STEP06_association_minus" style="cursor:pointer;color:red;"></span>';
        var $association_html = $(association_html);
        association_num += 1;

        $association_html.find('#STEP06_association_no').text("Association No."+association_num.toString());
        $association_html.find('#STEP06_association_no').after(association_minus_html);
        $association_html.insertBefore('#association_above');
    }

    function minusAssociation() {
        $(this).parent().parent().remove();
    }

    function addAssociationColumn() {
        var column_minus_html = '<th style="text-align:right;"><span class="btn glyphicon glyphicon-minus STEP06_column_minus" style="cursor:pointer;color:red;"></span></th>';
        var $table = $(this).parent().parent().parent().parent();

        $table.find('thead tr th').last().after(column_minus_html);
        $table.find('tbody tr').each(function() {
            var input_html = $(this).find('td:nth-child(2)').prop('outerHTML');
            $(this).find('td').last().after(input_html);
        });
    }

    function minusAssociationColumn() {
        var index = $(this).parent().parent().find('th').index($(this).parent());
        var $table = $(this).parent().parent().parent().parent();

        $table.find('thead tr th:nth-child('+(index+1).toString()+')').remove();
        $table.find('tbody tr').each(function() {
            $(this).find('td:nth-child('+(index+1).toString()+')').remove();
        });
    }

    function addAssociationRow() {
        var row_minus_html = '<span class="btn glyphicon glyphicon-minus STEP06_row_minus" style="cursor:pointer;color:red;"></span>';
        var $table = $(this).parent().parent().parent().parent();
        var $row_html = $(association_row_html);

        $row_html.find('td').first().html(row_minus_html);
        $table.find('tbody tr').last().after($row_html.prop('outerHTML'));
    }

    function minusAssociationRow() {
        $(this).parent().parent().remove();
    }

    function submit() {
        $.confirm({
            title: ' ',
            content: 'Submit now?',
            buttons: {
                yes: function () {
                    content.step_now = 7;
                    querySubmit({
                        'kb': 'SNP',
                        'action': 'submit',
                        'content' : JSON.stringify(content)
                    }, 7, 'submit');
                },
                later: function () {
                },
            },
            theme: 'bootstrap',
        });
    }

    function reviewSubmit() {
        if (content.no_flag) {
            content.no_flag = false;
        } else {
            $('#review_alert').show();
        }

        //Jump to step now
        $("#STEP0"+(step_now).toString()+"_nav").trigger("click");
        //disable STEP01
        $("#STEP01_nav").parent().addClass("disabled");
        $("#STEP01_nav").prop("data-toggle", null);
        //remove STEP02's back
        $("#STEP02_back").remove();
        //fill STEP02's url
        //fill & disable STEP02's pubmed_id
        $("#STEP02_form input[name=url]").val("https://www.ncbi.nlm.nih.gov/pubmed/"+content.STEP01.pubmed_id.toString());
        $("#STEP02_form input[name=pubmed_id]").val(content.STEP01.pubmed_id);
        freezePubmedId();

        //fill STEP02
        if ('STEP02' in content) {
            $("#STEP02_form :input").each(function() {
                var name = $(this).attr("name");
                if (name != 'pubmed_id') {
                    $(this).val(content.STEP02[name]);
                }
            });
        } else { console.log('REVIEW:NO STEP02'); }
        //fill Paper upload
        if (content.paper_uploaded) {
            var paper_name = content.paper_name;
            var paper_size = content.paper_size;
            var paper_link = content.paper_link;

            $('#STEP02_paper_table').css('opacity', 1);
            $('#STEP02_paper_filename').text(paper_name);
            $('#STEP02_paper_size').text(paper_size.toString()+" MB");
            $('#STEP02_paper_download').show();
            $('#STEP02_paper_download').attr('href', paper_link);
        } else { console.log('REVIEW:NO PAPER UPLOAD'); }
        //fill STEP03
        if ('STEP03' in content) {
            var tumors = content.STEP03.tumor;
            for (var i = 1; i < tumors.length; i++) {
                $('#STEP03_tumor_add').trigger("click");
            }
            var i_tumor = 0;
            $("#STEP03_form .STEP03_tumor").each(function() {
                var tumor_vals = tumors[i_tumor];
                $(":input", this).each(function() {
                    var name = $(this).attr("name");
                    $(this).val(tumor_vals[name]);
                });
                i_tumor += 1;
            });
        } else { console.log('REVIEW:NO STEP03'); }
        //fill STEP04
        recur_step04 = 1;
        if ('STEP04' in content) {
            genStep04()

            var i_tumor = 0;
            $("#STEP04_form .STEP04_tumor").each(function() {
                var variants = content.STEP04.variant[i_tumor];
                for (var i = 1; i < variants.length; i++) {
                    $('.STEP04_variant_add', this).trigger("click");
                }
                var i_variant = 0
                $(".STEP04_variant", this).each(function() {
                    var variant_vals = variants[i_variant];
                    if (variant_vals['new']) {
                        $('.STEP04_gene_new', this).trigger("click");
                    }
                    $(":input", this).each(function() {
                        var name = $(this).attr("name");
                        $(this).val(variant_vals[name]);
                    });
                    i_variant += 1;
                });
                i_tumor += 1;
            });
        } else { console.log('REVIEW:NO STEP04'); }
        //fill STEP05
        if ('STEP05' in content) {
            var prognoses = content.STEP05.prognosis;
            for (var i = 1; i < prognoses.length; i++) {
                $('#STEP05_prognosis_add').trigger("click");
            }
            var i_prognosis = 0;
            $("#STEP05_form .STEP05_prognosis").each(function() {
                var prognosis_vals = prognoses[i_prognosis];
                var subgroups = prognosis_vals.subgroup;
                for (var i = 1; i < subgroups.length; i++) {
                    $('.STEP05_subgroup_add', this).trigger("click");
                }
                var i_subgroup = 0;
                $(":input", this).each(function() {
                    var name = $(this).attr("name");
                    if (name != 'subgroup') {
                        $(this).val(prognosis_vals[name]);
                    } else {
                        $(this).val(subgroups[i_subgroup]);
                        i_subgroup += 1
                    }
                });
                i_prognosis += 1;
            });
        } else { console.log('REVIEW:NO STEP05'); }
        //fill STEP06
        recur_step06 = 1;
        if ('STEP06' in content) {
            genStep06()

            var associations = content.STEP06.association;
            for (var i = 1; i < associations.length; i++) {
                $('#STEP06_association_add').trigger("click");
            }

            i_association = 0;
            $("#STEP06_form .STEP06_association").each(function() {
                associations_ = associations[i_association];
                select_order = ['tumor', 'gene', 'variant', 'prognosis', 'subgroup'];
                for (var i = 0; i < select_order.length; i++) {
                    var name = select_order[i];
                    $('select[name='+name+']', this).val(associations_[0][name]).trigger("change");
                }

                for (var i = 1; i < associations_.length; i++) {
                    $('.STEP06_row_add', this).trigger("click");
                }

                i_row = 0
                $(".STEP06_association_genotype tbody tr", this).each(function() {
                    $(":input", this).each(function() {
                        var name = $(this).attr("name");
                        $(this).val(associations_[i_row][name]);
                    });
                    i_row += 1;
                });
                i_association += 1;
            });
        } else { console.log('REVIEW:NO STEP06'); }

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
