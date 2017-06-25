from django.shortcuts import render


def index(request):
    stats = {'research_num': 201, 'gene_num': 199, 'variant_num': 782, 'case_num': 5013}
    context = {'stats': stats}
    return render(request, 'index.html', context)
