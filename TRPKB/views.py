from django.http import HttpResponse, Http404
from django.shortcuts import render

from KB.models import Association


def index(request):
    stats = {'research_num': 201, 'gene_num': 199, 'variant_num': 782, 'case_num': 5013}
    context = {'stats': stats}
    return render(request, 'index.html', context)


def search(request):
    context = {'num': None, 'desc': None, 'dt_data': []}
    try:
        gene = request.GET['gene']
        variant = request.GET['variant']
        disease = request.GET['disease']

        results = Association.objects.filter(
            disease__disease__contains=disease).filter(
            variant__gene__gene_official_symbol__contains=gene).filter(
            variant__variant_dbsnp__contains=variant)

        if len(results) == 0:
            context['num'] = 0
            context['desc'] = ", Please refine your key words."
        else:
            context['num'] = len(results)
            context['desc'] = ""
            for i, r in enumerate(results):
                row = [i + 1, r.research.title, r.disease.disease,
                       "r.research.treatment_type.treatment_type",
                       r.prognosis.prognosis,
                       r.variant.gene.gene_official_symbol,
                       r.variant.variant_dbsnp,
                       r.genotype]
                context['dt_data'].append(row)

    except Exception as e:
        raise e

    return render(request, 'search_results.html', context)
