from django.contrib import admin

from .models import *

admin.site.register(Tumor)
admin.site.register(Gene)
admin.site.register(EvidenceBasedMedicineLevel)
admin.site.register(Research)
admin.site.register(Prognosis)
admin.site.register(Subgroup)
admin.site.register(Association)
