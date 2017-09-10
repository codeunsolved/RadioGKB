#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import locale
import json
import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.shortcuts import render

from KB_SNP.models import Tumor as T_Snp
from KB_SNP.models import Gene as G_Snp
from KB_SNP.models import Variant as V_Snp
from KB_SNP.models import EvidenceBasedMedicineLevel as E_Snp
from KB_SNP.models import Research as R_Snp
from KB_SNP.models import Prognosis as P_Snp
from KB_SNP.models import Subgroup as S_Snp
from KB_SNP.models import Association as A_Snp
from KB_Exp.models import Tumor as T_Exp
from KB_Exp.models import Gene as G_Exp
from KB_Exp.models import EvidenceBasedMedicineLevel as E_Exp
from KB_Exp.models import Research as R_Exp
from KB_Exp.models import Prognosis as P_Exp
from KB_Exp.models import Subgroup as S_Exp
from KB_Exp.models import Association as A_Exp
from Submit.models import Draft

from .importData import read_xls


def view_locale(request):
    loc_info = "getlocale: {}<br/>getdefaultlocale: {}<br/>".format(
               str(locale.getlocale()), str(locale.getdefaultlocale()))
    loc_info += "getfilesystemencoding: {}<br/>getdefaultencoding: {}".format(
                str(sys.getfilesystemencoding()), str(sys.getdefaultencoding()))
    return HttpResponse(loc_info)


def get_stats():
    return {'r_snp_num': len(R_Snp.objects.all()),
            'g_snp_num': len(G_Snp.objects.all()),
            'v_snp_num': len(V_Snp.objects.all()),
            'r_exp_num': len(R_Exp.objects.all()),
            'g_exp_num': len(G_Exp.objects.all())}


def index(request):
    context = {'stats': get_stats(), 'genes': G_Snp.objects.all()}
    return render(request, 'index.html', context)


def about(request):
    context = {'stats': get_stats()}
    return render(request, 'about.html', context)


def access(request):
    context = {'stats': get_stats()}
    return render(request, 'access.html', context)


def submit(request):
    context = {'stats': get_stats()}
    return render(request, 'submit.html', context)


def news(request):
    context = {'stats': get_stats()}
    return render(request, 'news.html', context)


def profile(request):
    return render(request, 'profile.html')


@login_required
def submit_query(request):
    def get_status_html(status, content):
        if status in ['Revison', 'Rejected']:
            status_html = '<strong style="color: red;">{}</strong>'.format(status)
        elif status == 'Accepted':
            status_html = '<strong style="color: green;">{}</strong>'.format(status)
        else:
            status_html = '<strong>{}</strong>'.format(status)

        if 'comments' in content:
            status_html += '<br><span>{}</span>'.format(content['comments'])

        return status_html

    def get_last_change(content):
        return "{} by {}".format(content['log'][-1]['time'][:19],
                                 content['log'][-1]['user'])

    response = {'data': []}
    try:
        tab = request.POST['tab']

        username = request.user.username

        if tab == 'draft':
            results = Draft.objects.filter(user__username=username).exclude(status='Accepted')
            for i, r in enumerate(results):
                content = r.content

                if r.status == 'Under Review':
                    edit_link = '<a style="pointer-events:none;color:gray;">Edit</a>'
                    delete_link = '<a style="pointer-events:none;color:gray;">Delete</a>'.format(r.pk)
                else:
                    edit_link = '<a href="{}/add/{}">Edit</a></li>'.format(r.kb.lower(), r.pk)
                    delete_link = '<a class="draft_delete" submit_id="{}">Delete</a>'.format(r.pk)

                log_link = '<a class="log" submit_id="{}">Log</a>'.format(r.pk)

                action = "{}&nbsp;&nbsp;{}&nbsp;&nbsp;{}".format(edit_link, delete_link, log_link)

                row = [i + 1,
                       r.kb,
                       r.title,
                       get_status_html(r.status, content),
                       get_last_change(content),
                       action]
                response['data'].append(row)
        elif tab == 'accepted':
            results = Draft.objects.filter(user__username=username).filter(status='Accepted')
            for i, r in enumerate(results):
                content = r.content

                log_link = '<a class="log" submit_id="{}">Log</a>'.format(r.pk)

                row = [i + 1,
                       r.kb,
                       r.title,
                       get_status_html(r.status, content),
                       "{}&nbsp;&nbsp;{}".format(get_last_change(content), log_link)]
                response['data'].append(row)
        elif tab == 'pending':
            results = Draft.objects.exclude(status__in=['Draft', 'Accepted'])
            for i, r in enumerate(results):
                content = r.content

                edit_link = '<a href="{}/add/{}">View</a>'.format(r.kb.lower(), r.pk)

                approve_link = '<a class="pending_action" submit_id="{}">Approve</a>'.format(r.pk)

                log_link = '<a class="log" submit_id="{}">Log</a>'.format(r.pk)

                action = "{}&nbsp;&nbsp;{}&nbsp;&nbsp;{}".format(edit_link, approve_link, log_link)

                row = [i + 1,
                       r.kb,
                       r.title,
                       r.user.username,
                       get_status_html(r.status, content),
                       get_last_change(content),
                       action]
                response['data'].append(row)
        elif tab == 'approved':
            results = Draft.objects.filter(status='Accepted')
            for i, r in enumerate(results):
                content = r.content

                log_link = '<a class="log" submit_id="{}">Log</a>'.format(r.pk)

                row = [i + 1,
                       r.kb,
                       r.title,
                       r.user.username,
                       "{}&nbsp;&nbsp;{}".format(get_last_change(content), log_link)]
                response['data'].append(row)

    except Exception as e:
        raise e

    return HttpResponse(json.dumps(response), content_type="application/json")


@login_required
def submit_add(request):
    def import_research(content):
        pk_d = {'prog': {}, 'sub': {}}
        # import Research
        step02 = content['STEP02']
        if step02['age_range_0'] and step02['age_range_1']:
            age_range = [float(step02['age_range_0']), float(step02['age_range_1'])]
        else:
            age_range = None

        ebml = E_Snp.objects.get(ebml=step02['ebml'])
        research, created = R_Snp.objects.get_or_create(
            title=step02['title'],
            language=step02['language'],
            pub_year=int(step02['pub_year']),
            pubmed_id=int(step02['pubmed_id']),
            url=step02['url'] if step02['url'] else None,
            pub_type=step02['pub_type'],
            ebml=ebml,
            ethnicity=step02['ethnicity'] if step02['ethnicity'] else None,
            patient_number=int(step02['patient_number']),
            male=int(step02['male']) if step02['male'] else None,
            female=int(step02['female']) if step02['female'] else None,
            median_age=float(step02['median_age']) if step02['median_age'] else None,
            mean_age=float(step02['mean_age']) if step02['mean_age'] else None,
            age_range=age_range,
            treatment_desc=step02['treatment_desc'] if step02['treatment_desc'] else None,
            treatment_type=step02['treatment_type'] if step02['treatment_type'] else None)

        # import Tumor
        step03 = content['STEP03']
        for row in step03['tumor']:
            T_Snp.objects.get_or_create(name=row['tumor'])

        # import Gene & Variant
        step04 = content['STEP04']
        for row1 in step04['variant']:
            for row2 in row1:
                gene_name = row2['gene']
                if row2['new']:
                    gene_name = row2['gene_new']

                if gene_name != '- N/A -':
                    gene, created = G_Snp.objects.get_or_create(gene_official_symbol=gene_name)
                    if row2['entrez_id']:
                        gene.entrez_gene_id = int(row2['entrez_id'])
                        gene.save()
                else:
                    gene = None

                V_Snp.objects.get_or_create(gene=gene, dbsnp=row2['dbsnp'])

        # import Prognosis
        step05 = content['STEP05']
        for row in step05['prognosis']:
            prognosis, created = P_Snp.objects.get_or_create(
                prognosis_name=row['prognosis_name'],
                prognosis_type=row['prognosis_type'] if row['prognosis_type'] else None,
                endpoint=row['endpoint'] if row['endpoint'] else None,
                original=row['original'],
                case_meaning=row['case_meaning'] if row['case_meaning'] else None,
                control_meaning=row['control_meaning'] if row['control_meaning'] else None,
                total_meaning=row['total_meaning'] if row['total_meaning'] else None,
                annotation=row['annotation'] if row['annotation'] else None)

            pk_d['prog'][row['prognosis_name']] = prognosis.pk

            for sub in row['subgroup']:
                if sub:
                    subgroup, created = S_Snp.objects.get_or_create(prognosis=prognosis, subgroup=sub)

                    if row['prognosis_name'] not in pk_d['sub']:
                        pk_d['sub'][row['prognosis_name']] = {}
                    pk_d['sub'][row['prognosis_name']][sub] = subgroup.pk

        # import Association
        step06 = content['STEP06']
        for row1 in step06['association']:
            for row in row1:
                tumor = T_Snp.objects.get(name=row['tumor'])
                print(row['variant'])
                variant = V_Snp.objects.get(dbsnp=row['variant'])
                prognosis = P_Snp.objects.get(pk=pk_d['prog'][row['prognosis']])
                if row['subgroup'] != '- N/A -':
                    subgroup = S_Snp.objects.get(pk=pk_d['sub'][row['prognosis']][row['subgroup']])
                else:
                    subgroup = None

                if row['ci_u_95_0'] and row['ci_u_95_1']:
                    ci_u_95 = [float(row['ci_u_95_0']), float(row['ci_u_95_1'])]
                else:
                    ci_u_95 = None
                if row['ci_m_95_0'] and row['ci_m_95_1']:
                    ci_m_95 = [float(row['ci_m_95_0']), float(row['ci_m_95_1'])]
                else:
                    ci_m_95 = None

            A_Snp.objects.get_or_create(
                research=research,
                tumor=tumor,
                variant=variant,
                prognosis=prognosis,
                subgroup=subgroup,
                genotype=row['genotype'],
                case_number=int(row['case_number']) if row['case_number'] else None,
                control_number=int(row['control_number']) if row['control_number'] else None,
                total_number=int(row['total_number']) if row['total_number'] else None,
                or_u=float(row['or_u']) if row['or_u'] else None,
                hr_u=float(row['hr_u']) if row['hr_u'] else None,
                rr_u=float(row['rr_u']) if row['rr_u'] else None,
                ci_u_95=ci_u_95,
                p_u=row['p_u'] if row['p_u'] else None,
                or_m=float(row['or_m']) if row['or_m'] else None,
                hr_m=float(row['hr_m']) if row['hr_m'] else None,
                rr_m=float(row['rr_m']) if row['rr_m'] else None,
                ci_m_95=ci_m_95,
                p_m=row['p_m'] if row['p_m'] else None)

    dup_msg = {1: "We already had this paper in KB-SNP! Please choose another.",
               2: "You already submitted/saved this paper! Please check your Draft box.",
               3: "Someone has been submited this paper already! Please choose another."}

    response = {}

    username = request.user.username
    action = request.POST['action']
    if action in ['save', 'next', 'submit']:
        try:
            kb = request.POST['kb']
            content = json.loads(request.POST['content'])
            step_now = content['step_now']

            if kb == 'SNP':
                if step_now == 1:
                    submitter = username
                    pubmed_id = int(content['STEP01']['pubmed_id'])

                    dup = 0
                    if R_Snp.objects.filter(pubmed_id=pubmed_id).first():
                        dup = 1
                    elif Draft.objects.filter(
                            pubmed_id=pubmed_id, user__username=submitter).first():
                        dup = 2
                    elif Draft.objects.filter(
                            pubmed_id=pubmed_id).exclude(status__in=['Draft', 'Rejected']).first():
                        dup = 3

                    if dup:
                        response['code'] = 0
                        response['msg'] = dup_msg[dup]
                    else:
                        content_ = {'time': {}, 'log': []}

                        content_['time']['create'] = str(datetime.datetime.now())
                        content_['log'].append({'user': username, 'step_now': step_now,
                                                'action': 'create',
                                                'time': str(datetime.datetime.now())})
                        content_['content'] = content

                        user = User.objects.get(username=submitter)
                        record = Draft.objects.create(user=user,
                                                      status='Draft',
                                                      kb='SNP',
                                                      pubmed_id=pubmed_id,
                                                      content=content_)
                        record.content['content']['submit_id'] = record.pk
                        record.save()

                        response['code'] = 1
                        response['submit_id'] = record.pk
                else:
                    submit_id = int(content['submit_id'])
                    record = Draft.objects.get(pk=submit_id)
                    submitter = record.user.username

                    if content['step_max'] < step_now:
                        content['step_max'] = step_now

                    record.content['log'].append({'user': username, 'step_now': step_now,
                                                  'action': action,
                                                  'time': str(datetime.datetime.now())})

                    record.content['content'] = content

                    if step_now == 2:
                        title = content['STEP02']['title'].strip()
                        record.title = title

                    elif step_now == 7:
                        record.content['time']['submit'] = str(datetime.datetime.now())
                        record.status = 'Under Review'

                    record.save()
                    response['code'] = 1

        except Exception as e:
            response['code'] = 0
            response['msg'] = str(e)

    elif action in ['upload']:
        try:
            submit_id = int(request.POST['submit_id'])
            paper_file = request.FILES['paper']

            record = Draft.objects.get(pk=submit_id)

            paper_file.name = "{}_{}".format(record.content['content']['STEP01']['pubmed_id'], paper_file.name)
            paper_name = paper_file.name
            paper_size = round(paper_file.size / 1000 / 1000, 3)

            error_msg = []
            if paper_size > 20:
                error_msg.append("Uploading paper exceeds the maximum upload size: 20MB")
            if not re.search('\.(pdf|zip)$', paper_name):
                error_msg.append("Uploading paper only accepts pdf/zip format")

            if len(error_msg) > 0:
                record.content['log'].append({'user': username,
                                              'msg': "ERROR: {}<br>{} | {}MB".format(
                                                  '<br>'.join(error_msg), paper_name, paper_size),
                                              'action': 'paper upload',
                                              'time': str(datetime.datetime.now())})

                response['error'] = '<br>'.join(error_msg)
            else:
                if record.paper:
                    record.paper.delete()
                record.paper = paper_file

                record.save()  # then record.paper.url will update

                record.content['content']['paper_uploaded'] = True
                record.content['content']['paper_name'] = paper_name
                record.content['content']['paper_size'] = paper_size
                record.content['content']['paper_link'] = record.paper.url

                record.content['log'].append({'user': username,
                                              'msg': "{} | {}MB".format(paper_name, paper_size),
                                              'action': 'paper upload',
                                              'time': str(datetime.datetime.now())})

                record.save()

                response['url'] = record.paper.url

        except Exception as e:
            raise e

    elif action in ['Revision', 'Accepted', 'Rejected']:
        try:
            submit_id = int(request.POST['submit_id'])
            comments = request.POST['comments']

            record = Draft.objects.get(pk=submit_id)

            record.content['comments'] = comments
            record.status = action
            record.content['log'].append({'user': username, 'comments': comments,
                                          'action': action,
                                          'time': str(datetime.datetime.now())})

            record.save()

            if action == 'Accepted':
                try:
                    import_research(record.content['content'])
                    msg = 'Success'
                    record.content['log'].append({'user': username, 'msg': msg,
                                                  'action': 'import',
                                                  'time': str(datetime.datetime.now())})

                    record.save()
                except Exception as e:
                    record.status = 'Revision'
                    record.content['comments'] += '!IMPORT ERROR!'
                    msg = 'Error: {}'.format(e)
                    record.content['log'].append({'user': username, 'msg': msg,
                                                  'action': 'import',
                                                  'time': str(datetime.datetime.now())})

                    record.save()
                    raise e

            response['code'] = 1
        except Exception as e:
            response['code'] = 0
            raise e

    elif action in ['Delete']:
        try:
            submit_id = int(request.POST['submit_id'])

            Draft.objects.get(pk=submit_id).delete()

            response['code'] = 1
        except Exception as e:
            response['code'] = 0
            response['msg'] = str(e)

    elif action in ['Log']:
        try:
            submit_id = int(request.POST['submit_id'])

            response = {'data': []}

            log = Draft.objects.get(pk=submit_id).content['log']

            for row in log:
                time_ = row['time'][:19]
                user = row['user']
                action = row['action']
                note = ''

                if 'step_now' in row:
                    note = "at STEP0{}".format(row['step_now'])
                elif 'comments' in row:
                    note = "comments: {}".format(row['comments'])
                elif 'msg' in row:
                    note = row['msg']

                response['data'].append([time_, user, action, note])
        except Exception as e:
            raise e

    return HttpResponse(json.dumps(response), content_type="application/json")


@login_required
def snp_add(request, submit_id):
    context = {'stats': get_stats(), 'submit_id': None, 'content': {}}
    forms = {'research': {}}

    forms['research']['ebml'] = [x.ebml for x in E_Snp.objects.all()]
    genes = [x.gene_official_symbol for x in G_Snp.objects.all()] + ['- N/A -']

    context['forms'] = forms
    context['genes'] = genes

    if submit_id == 'new':
        context['review'] = 'false'
        context['submit_id'] = 0
        context['content'] = json.dumps({'step_now': 1, 'step_max': 1})
    else:
        result = Draft.objects.get(pk=int(submit_id))
        username = result.user.username
        content = result.content
        if request.user.is_staff or request.user.username == username:
            context['review'] = 'true'

            if content['content']['step_max'] == 1:
                content['content']['no_flag'] = 'true'
                content['content']['step_now'] = 2
                content['content']['step_max'] = 2

            if 'submit_id' not in content['content']:
                content['content']['submit_id'] = submit_id

            context['content'] = json.dumps(content['content']).replace("\\", r"\\").replace("'", r"\'")
        else:
            raise Http404
    return render(request, 'snp_add.html', context)


def snp_search(request):
    context = {'stats': get_stats(), 'num': None, 'desc': None, 'dt_data': []}
    try:
        term_gene = request.POST['gene']
        term_variant = request.POST['variant']
        term_tumor = request.POST['tumor']

        if term_gene:
            results = A_Snp.objects.filter(
                tumor__name__icontains=term_tumor).filter(
                variant__dbsnp__icontains=term_variant).filter(
                variant__gene__gene_official_symbol__icontains=term_gene)
        else:
            results = A_Snp.objects.filter(
                tumor__name__icontains=term_tumor).filter(
                variant__dbsnp__icontains=term_variant)

        if len(results) == 0:
            context['num'] = 0
            context['desc'] = ", Please refine your key words."
        else:
            row_data = {}
            for i, r in enumerate(results):
                tumor = r.tumor.name
                gene = r.variant.gene.gene_official_symbol if r.variant.gene else ''
                variant = r.variant.dbsnp
                tumor_id = r.tumor.pk
                variant_id = r.variant.pk
                key = "{}-{}-{}".format(tumor, gene, variant)
                if key not in row_data:
                    row_data[key] = {'tumor': tumor, 'tumor_id': tumor_id, 'gene': gene,
                                     'variant': variant, 'variant_id': variant_id, 'research': set()}
                row_data[key]['research'].add((r.research.title, r.research.pk))
            for i, (k, v) in enumerate(row_data.items()):
                research = ""
                for title, pk in v['research']:
                    research += "<p><a href=\"/snp/details/{}/{}/{}\">{}</a></p>".format(
                        pk, v['tumor_id'], v['variant_id'], title)
                row = [i + 1,
                       v['gene'],
                       v['variant'],
                       v['tumor'],
                       research]
                context['dt_data'].append(row)

            context['num'] = len(row_data)
            context['desc'] = ""

    except Exception as e:
        raise e

    return render(request, 'search_results.html', context)


def snp_details(request, research_id, tumor_id, variant_id):
    context = {'stats': get_stats(),
               'research': {}, 'tumor': {}, 'variant': {}, 'gene': {},
               'tabs': {'tab': [], 'content': {}}}

    research = R_Snp.objects.get(pk=research_id)
    context['research'] = {'title': research.title, 'pub_year': research.pub_year,
                           'pubmed_id': research.pubmed_id if research.pubmed_id else '',
                           'url': research.url if research.url else '',
                           'ebml': research.ebml,
                           'ethnicity': research.ethnicity if research.ethnicity else '',
                           'patient_number': research.patient_number,
                           'treatment_type': research.treatment_type if research.treatment_type else '',
                           }

    tumor = T_Snp.objects.get(pk=tumor_id)
    context['tumor']['name'] = tumor.name

    variant = V_Snp.objects.get(pk=variant_id)
    context['variant']['dbsnp'] = variant.dbsnp

    gene = variant.gene
    if gene:
        context['gene']['name'] = gene.gene_official_symbol
        context['gene']['id'] = gene.entrez_gene_id if gene.entrez_gene_id else ''
        context['gene']['alias'] = ', '.join(gene.gene_alternative_symbols) if gene.gene_alternative_symbols else ''
        context['gene']['full_name'] = gene.gene_official_full_name if gene.gene_official_full_name else ''
        context['gene']['type'] = gene.gene_type if gene.gene_type else ''
        context['gene']['summary'] = gene.gene_summary if gene.gene_summary else ''
    else:
        context['gene']['name'] = ''
        context['gene']['id'] = ''
        context['gene']['alias'] = ''
        context['gene']['full_name'] = ''
        context['gene']['type'] = ''
        context['gene']['summary'] = ''

    association = A_Snp.objects.filter(research__pk=research_id, tumor__pk=tumor_id, variant__pk=variant_id)

    prognosis = {}
    for row in association:
        p_id = row.prognosis.pk
        name = row.prognosis.prognosis_name
        if p_id not in prognosis:
            prognosis[p_id] = name

    for p_id in prognosis:
        context['tabs']['tab'].append({'p_id': p_id, 'name': prognosis[p_id]})

        subgroups = {}
        a_p = association.filter(prognosis__pk=p_id).order_by('pk')
        for row in a_p:
            cols = ['genotype',
                    'case_number', 'control_number', 'total_number',
                    'or_u', 'hr_u', 'rr_u', 'ci_u_95', 'p_u',
                    'or_m', 'hr_m', 'rr_m', 'ci_m_95', 'p_m']

            if row.subgroup:
                subgroup_name = row.subgroup.subgroup
            else:
                subgroup_name = ''
            if subgroup_name not in subgroups:
                subgroups[subgroup_name] = {'stats': {}, 'thead': [], 'tbody': []}

            sub_stats = subgroups[subgroup_name]['stats']

            def get_or_empty(key):
                def handle_range(string):
                    ranges = re.findall("Decimal\('([\d\.]+)'\)", string)
                    return "[{}, {}]".format(ranges[0], ranges[1])

                val = getattr(row, key)
                if val and key in ['ci_u_95', 'ci_m_95']:
                    val = handle_range(val.__str__())

                if key not in sub_stats:
                    sub_stats[key] = 0

                if val:
                    sub_stats[key] += 1
                    return val
                else:
                    return ''

            sub_row = {'genotype': row.genotype}
            for col in cols:
                sub_row[col] = get_or_empty(col)
            subgroups[subgroup_name]['tbody'].append(sub_row)

        for subgroup_name in subgroups:
            trows = [[] for x in subgroups[subgroup_name]['tbody']]
            for col in cols:
                if subgroups[subgroup_name]['stats'][col] > 1:
                    subgroups[subgroup_name]['thead'].append(col)
                    for i, row in enumerate(subgroups[subgroup_name]['tbody']):
                        trows[i].append(row[col])
            subgroups[subgroup_name]['tbody'] = trows

        annotation = P_Snp.objects.get(pk=p_id).annotation
        context['tabs']['content'][p_id] = {'subgroups': subgroups,
                                            'annotation': annotation if annotation else None}

    return render(request, 'snp_details.html', context)


def import_snp(request):
    def get_via_pk(pk, data, i=1):
        for row in data:
            if row[0] == pk:
                return row[i]
        return None

    msg = ""
    if 'path' in request.GET and 'table' in request.GET:
        try:
            path = request.GET['path']
            table = request.GET['table']

            data = read_xls(path, 'snp')

            if re.search('research', table) or re.search('all', table):
                for ebml in ['Systematic Review', 'Randomized Controlled Trial', 'Cohort Study', 'Case Control Study',
                             'Case Series', 'Case Report', 'Animal Assay', 'Cell Line Study']:
                    E_Snp.objects.get_or_create(ebml=ebml)

                for row in data['research']:
                    pubmed_id = int(row[4]) if row[4] else None
                    ebml = E_Snp.objects.get(ebml=row[7])
                    ethnicity = row[8] if row[8] else None
                    male = int(row[10]) if row[10] else None
                    female = int(row[11]) if row[11] else None
                    median_age = float(row[12]) if row[12] else None
                    mean_age = float(row[13]) if row[13] else None
                    age_range = [float(x) for x in row[14].split('-')] if row[14] else None
                    treatment_desc = row[15] if row[15] else None
                    treatment_type = row[16] if row[16] else None
                    R_Snp.objects.get_or_create(title=row[1], language=row[2], pub_year=int(row[3]),
                                                pubmed_id=pubmed_id, url=row[5], pub_type=row[6], ebml=ebml,
                                                ethnicity=ethnicity, patient_number=int(row[9]),
                                                male=male, female=female,
                                                median_age=median_age, mean_age=mean_age, age_range=age_range,
                                                treatment_desc=treatment_desc, treatment_type=treatment_type)

            if re.search('tumor', table) or re.search('all', table):
                for row in data['tumor']:
                    T_Snp.objects.get_or_create(name=row[1])

            if re.search('gene', table) or re.search('all', table):
                for row in data['gene']:
                    G_Snp.objects.get_or_create(gene_official_symbol=row[1],
                                                entrez_gene_id=int(row[2]),
                                                gene_alternative_symbols=row[3].split(';'),
                                                gene_official_full_name=row[4],
                                                gene_type=row[5],
                                                gene_summary=row[6])

            if re.search('variant', table) or re.search('all', table):
                for row in data['variant']:
                    gene = G_Snp.objects.get(gene_official_symbol=get_via_pk(row[1], data['gene'])) if row[1] else None
                    V_Snp.objects.get_or_create(gene=gene, dbsnp=row[2])

            if re.search('prognosis', table) or re.search('all', table):
                for row in data['prognosis']:
                    prognosis_type = row[2] if row[2] else None
                    endpoint = row[3] if row[3] else None
                    case_meaning = row[5] if row[5] else None
                    control_meaning = row[6] if row[6] else None
                    total_meaning = row[7] if row[7] else None
                    annotation = row[9] if row[9] else None
                    P_Snp.objects.create(prognosis_name=row[1], prognosis_type=prognosis_type,
                                         endpoint=endpoint, original=row[4],
                                         case_meaning=case_meaning, control_meaning=control_meaning,
                                         total_meaning=total_meaning, annotation=annotation)

            if re.search('subgroup', table) or re.search('all', table):
                for row in data['subgroup']:
                    prognosis = P_Snp.objects.get(pk=int(row[1]))
                    S_Snp.objects.get_or_create(prognosis=prognosis, subgroup=row[2])

            if re.search('association', table) or re.search('all', table):
                for row in data['association']:
                    research = R_Snp.objects.get(title=get_via_pk(row[1], data['research']))
                    tumor = T_Snp.objects.get(name=get_via_pk(row[2], data['tumor']))
                    variant = V_Snp.objects.get(dbsnp=get_via_pk(row[4], data['variant'], 2))
                    prognosis = P_Snp.objects.get(pk=int(row[5]))
                    subgroup = S_Snp.objects.get(pk=int(row[6])) if row[6] else None
                    case_number = int(row[8]) if row[8] else None
                    control_number = int(row[9]) if row[9] else None
                    total_number = int(row[10]) if row[10] else None
                    or_u = float(row[11]) if row[11] else None
                    hr_u = float(row[12]) if row[12] else None
                    rr_u = float(row[13]) if row[13] else None
                    ci_u_95 = [float(x) for x in row[14].split('-')] if row[14] else None
                    p_u = row[15] if row[15] else None
                    or_m = float(row[16]) if row[16] else None
                    hr_m = float(row[17]) if row[17] else None
                    rr_m = float(row[18]) if row[18] else None
                    ci_m_95 = [float(x) for x in row[19].split('-')] if row[19] else None
                    p_m = row[20] if row[20] else None
                    try:
                        a = A_Snp.objects.get(research=research, tumor=tumor, variant=variant,
                                              prognosis=prognosis, subgroup=subgroup, genotype=row[7],
                                              case_number=case_number, control_number=control_number,
                                              total_number=total_number,
                                              or_u=or_u, hr_u=hr_u, rr_u=rr_u, ci_u_95=ci_u_95, p_u=p_u,
                                              or_m=or_m, hr_m=hr_m, rr_m=rr_m, ci_m_95=ci_m_95, p_m=p_m)
                        msg += "{} - {}<br>".format(a.pk, row)
                    except Exception as e:
                        pass

                    A_Snp.objects.create(research=research, tumor=tumor, variant=variant,
                                         prognosis=prognosis, subgroup=subgroup, genotype=row[7],
                                         case_number=case_number, control_number=control_number,
                                         total_number=total_number,
                                         or_u=or_u, hr_u=hr_u, rr_u=rr_u, ci_u_95=ci_u_95, p_u=p_u,
                                         or_m=or_m, hr_m=hr_m, rr_m=rr_m, ci_m_95=ci_m_95, p_m=p_m)

        except Exception as e:
            raise e

        return HttpResponse("OK!<br>" + msg)
    else:
        return render(request, 'import_data.html')


def import_exp(request):
    def get_via_pk(pk, data, i=1):
        for row in data:
            if row[0] == pk:
                return row[i]
        return None

    msg = ""
    if 'path' in request.GET and 'table' in request.GET:
        try:
            path = request.GET['path']
            table = request.GET['table']

            data = read_xls(path, 'exp')

            if re.search('research', table) or re.search('all', table):
                for ebml in ['Systematic Review', 'Randomized Controlled Trial', 'Cohort Study', 'Case Control Study',
                             'Case Series', 'Case Report', 'Animal Assay', 'Cell Line Study']:
                    E_Exp.objects.get_or_create(ebml=ebml)

                for row in data['research']:
                    pubmed_id = int(row[4]) if row[4] else None
                    ebml = E_Exp.objects.get(ebml=row[7])
                    ethnicity = row[8] if row[8] else None
                    male = int(row[10]) if row[10] else None
                    female = int(row[11]) if row[11] else None
                    median_age = float(row[12]) if row[12] else None
                    mean_age = float(row[13]) if row[13] else None
                    age_range = [float(x) for x in row[14].split('-')] if row[14] else None
                    exp_detection_method = row[15] if row[15] else None
                    cut_off_value = row[16] if row[16] else None
                    treatment_desc = row[17] if row[17] else None
                    treatment_type = row[18] if row[18] else None
                    R_Exp.objects.get_or_create(title=row[1], language=row[2], pub_year=int(row[3]),
                                                pubmed_id=pubmed_id, url=row[5], pub_type=row[6], ebml=ebml,
                                                ethnicity=ethnicity, patient_number=int(row[9]),
                                                male=male, female=female,
                                                median_age=median_age, mean_age=mean_age, age_range=age_range,
                                                exp_detection_method=exp_detection_method,
                                                cut_off_value=cut_off_value,
                                                treatment_desc=treatment_desc, treatment_type=treatment_type)

            if re.search('tumor', table) or re.search('all', table):
                for row in data['tumor']:
                    T_Exp.objects.get_or_create(name=row[1])

            if re.search('gene', table) or re.search('all', table):
                for row in data['gene']:
                    G_Exp.objects.get_or_create(gene_official_symbol=row[1],
                                                entrez_gene_id=int(row[2]),
                                                gene_alternative_symbols=row[3].split(';'),
                                                gene_official_full_name=row[4],
                                                gene_type=row[5],
                                                gene_summary=row[6])

            if re.search('prognosis', table) or re.search('all', table):
                for row in data['prognosis']:
                    prognosis_type = row[2] if row[2] else None
                    endpoint = row[3] if row[3] else None
                    case_meaning = row[5] if row[5] else None
                    control_meaning = row[6] if row[6] else None
                    total_meaning = row[7] if row[7] else None
                    annotation = row[8] if row[8] else None
                    P_Exp.objects.create(prognosis_name=row[1], prognosis_type=prognosis_type,
                                         endpoint=endpoint, original=row[4],
                                         case_meaning=case_meaning, control_meaning=control_meaning,
                                         total_meaning=total_meaning, annotation=annotation)

            if re.search('subgroup', table) or re.search('all', table):
                for row in data['subgroup']:
                    prognosis = P_Exp.objects.get(pk=int(row[1]))
                    S_Exp.objects.get_or_create(prognosis=prognosis, subgroup=row[2])

            if re.search('association', table) or re.search('all', table):
                for row in data['association']:
                    research = R_Exp.objects.get(title=get_via_pk(row[1], data['research']))
                    tumor = T_Exp.objects.get(name=get_via_pk(row[2], data['tumor']))
                    gene = G_Exp.objects.get(gene_official_symbol=get_via_pk(row[3], data['gene']))
                    prognosis = P_Exp.objects.get(pk=int(row[4]))
                    subgroup = S_Exp.objects.get(pk=int(row[5])) if row[5] else None
                    case_number = int(row[7]) if row[7] else None
                    control_number = int(row[8]) if row[8] else None
                    total_number = int(row[9]) if row[9] else None
                    or_u = float(row[10]) if row[10] else None
                    hr_u = float(row[11]) if row[11] else None
                    rr_u = float(row[12]) if row[12] else None
                    ci_u_95 = [float(x) for x in row[13].split('-')] if row[13] else None
                    p_u = row[14] if row[14] else None
                    or_m = float(row[15]) if row[15] else None
                    hr_m = float(row[16]) if row[16] else None
                    rr_m = float(row[17]) if row[17] else None
                    ci_m_95 = [float(x) for x in row[18].split('-')] if row[18] else None
                    p_m = row[19] if row[19] else None
                    try:
                        a = A_Exp.objects.get(research=research, tumor=tumor, gene=gene,
                                              prognosis=prognosis, subgroup=subgroup, expression=row[6],
                                              case_number=case_number, control_number=control_number,
                                              total_number=total_number,
                                              or_u=or_u, hr_u=hr_u, rr_u=rr_u, ci_u_95=ci_u_95, p_u=p_u,
                                              or_m=or_m, hr_m=hr_m, rr_m=rr_m, ci_m_95=ci_m_95, p_m=p_m)
                        msg += "{} - {}<br>".format(a.pk, row)
                    except Exception as e:
                        pass

                    A_Exp.objects.create(research=research, tumor=tumor, gene=gene,
                                         prognosis=prognosis, subgroup=subgroup, expression=row[6],
                                         case_number=case_number, control_number=control_number,
                                         total_number=total_number,
                                         or_u=or_u, hr_u=hr_u, rr_u=rr_u, ci_u_95=ci_u_95, p_u=p_u,
                                         or_m=or_m, hr_m=hr_m, rr_m=rr_m, ci_m_95=ci_m_95, p_m=p_m)

        except Exception as e:
            raise e

        return HttpResponse("OK!<br>" + msg)
    else:
        return render(request, 'import_data.html')
