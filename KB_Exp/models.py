from django.db import models
from django.contrib.postgres.fields import ArrayField, IntegerRangeField, FloatRangeField


class Tumor(models.Model):
    tumor_name = models.CharField(max_length=100, unique=True)
    mesh_term = models.CharField(max_length=50, unique=True, null=True, blank=True)
    mesh_id = models.IntegerField(unique=True, null=True, blank=True)
    tumor_type = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.tumor_name)


class Gene(models.Model):
    gene_official_symbol = models.CharField(max_length=50, unique=True)
    entrez_gene_id = models.IntegerField(unique=True, null=True, blank=True)
    gene_alternative_symbols = ArrayField(models.CharField(max_length=50), null=True, blank=True)
    gene_official_full_name = models.CharField(max_length=100, null=True, blank=True)
    gene_type = models.CharField(max_length=50, null=True, blank=True)
    gene_summary = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.gene_official_symbol)


class EvidenceBasedMedicineLevel(models.Model):
    ebml = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return "{}".format(self.ebml)


class Research(models.Model):
    title = models.CharField(max_length=500, unique=True)
    language = models.CharField(max_length=50)
    pub_year = models.IntegerField()
    pubmed_id = models.IntegerField(null=True, blank=True)
    url = models.URLField(max_length=500)
    pub_type = models.CharField(max_length=50)
    ebml = models.ForeignKey('KB_Exp.EvidenceBasedMedicineLevel')
    ethnicity = models.CharField(max_length=100, null=True, blank=True)
    patient_number = models.IntegerField(null=True, blank=True)
    male = models.IntegerField(null=True, blank=True)
    female = models.IntegerField(null=True, blank=True)
    median_age = models.FloatField(null=True, blank=True)
    mean_age = models.FloatField(null=True, blank=True)
    age_range = FloatRangeField(null=True, blank=True)
    exp_detection_method = models.CharField(max_length=100, null=True, blank=True)
    cut_off_value = models.TextField(null=True, blank=True)
    treatment_desc = models.TextField(null=True, blank=True)
    treatment_type = models.CharField(max_length=500, null=True, blank=True)
    journal = models.CharField(max_length=100, null=True, blank=True)
    abstract = models.TextField(null=True, blank=True)
    tumor_stage = tumor_stage = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.title)


class Prognosis(models.Model):
    prognosis_name = models.CharField(max_length=200)
    prognosis_type = models.CharField(max_length=50, null=True, blank=True)
    endpoint = models.CharField(max_length=200, null=True, blank=True)
    original = models.CharField(max_length=20)
    case_meaning = models.CharField(max_length=200, null=True, blank=True)
    control_meaning = models.CharField(max_length=200, null=True, blank=True)
    total_meaning = models.CharField(max_length=200, null=True, blank=True)
    annotation = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.prognosis_name)


class Subgroup(models.Model):
    prognosis = models.ForeignKey('KB_Exp.Prognosis')
    subgroup = models.CharField(max_length=200)

    def __str__(self):
        return "[{!s}]{}".format(self.prognosis, self.subgroup)


class Association(models.Model):
    research = models.ForeignKey('KB_Exp.Research')
    tumor = models.ForeignKey('KB_Exp.Tumor')
    gene = models.ForeignKey('KB_Exp.Gene')
    prognosis = models.ForeignKey('KB_Exp.Prognosis')
    subgroup = models.ForeignKey('KB_Exp.Subgroup', null=True, blank=True)
    expression = models.CharField(max_length=50)
    case_number = models.IntegerField(null=True, blank=True)
    control_number = models.IntegerField(null=True, blank=True)
    total_number = models.IntegerField(null=True, blank=True)
    or_u = models.FloatField(null=True, blank=True)
    hr_u = models.FloatField(null=True, blank=True)
    rr_u = models.FloatField(null=True, blank=True)
    ci_u_95 = FloatRangeField(null=True, blank=True)
    p_u = models.CharField(max_length=50, null=True, blank=True)
    or_m = models.FloatField(null=True, blank=True)
    hr_m = models.FloatField(null=True, blank=True)
    rr_m = models.FloatField(null=True, blank=True)
    ci_m_95 = FloatRangeField(null=True, blank=True)
    p_m = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return "No.{} [{!s}][{}]{}".format(self.pk, self.tumor, self.gene.gene_official_symbol, self.expression)
