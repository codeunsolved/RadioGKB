from django.contrib import admin

from .models import Disease, Gene, Variant, Treatment, EvidenceBasedMedicineLevel, Research
from .models import Prognosis, Subgroup, Association

admin.site.register(Disease)
admin.site.register(Gene)
admin.site.register(Variant)
admin.site.register(Treatment)
admin.site.register(EvidenceBasedMedicineLevel)
admin.site.register(Research)
admin.site.register(Prognosis)
admin.site.register(Subgroup)
admin.site.register(Association)
