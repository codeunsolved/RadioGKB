from django.db import models
from django.contrib.postgres.fields import ArrayField, IntegerRangeField, FloatRangeField


class Disease(models.Model):
    disease = models.CharField(max_length=50, unique=True)
    mesh_term = models.CharField(max_length=50, unique=True)
    mesh_id = models.IntegerField(unique=True)

    def __str__(self):
        return "{s}".format(self.mesh_term)


class Gene(models.Model):
    gene_official_symbol = models.CharField(max_length=50, unique=True)
    gene_alternative_symbols = ArrayField(models.CharField(max_length=50), blank=True)

    def __str__(self):
        return "{s}".format(self.gene)


class Variant(models.Model):
    gene = models.ForeignKey('TRPKB.Gene')
    variant_dbsnp = models.CharField(max_length=200)

    def __str__(self):
        return "[{!s}]{s}".format(self.gene, self.variant_dbsnp)


class Treatment(models.Model):
    treatment_type = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return "{s}".format(self.treatment_type)


class EvidenceBasedMedicineLevel(models.Model):
    ebml = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return "{s}".format(self.ebml)


class Research(models.Model):
    title = models.CharField(max_length=500, unique=True)
    language = models.CharField(max_length=50, null=True, blank=True)
    pub_year = models.IntegerField(null=True, blank=True)
    pub_type = models.CharField(max_length=50, null=True, blank=True)
    pubmed_id = models.IntegerField(null=True, blank=True)
    ebml = models.ForeignKey('TRPKB.ebml', null=True, blank=True)
    ethnicity = models.CharField(max_length=50, null=True, blank=True)
    patient_number = models.IntegerField(null=True, blank=True)
    male = models.IntegerField(null=True, blank=True)
    female = models.IntegerField(null=True, blank=True)
    median_age = models.FloatField(null=True, blank=True)
    mean_age = models.FloatField(null=True, blank=True)
    age_range = IntegerRangeField(blank=True)
    treatment_desc = models.TextField(null=True, blank=True)
    treatment_type = models.ForeignKey('TRPKB.Treatment', null=True, blank=True)


    def __str__(self):
        return "{s}".format(self.title)


class Prognosis(models.Model):
    research = models.ForeignKey('TRPKB.Reseach')
    disease = models.ForeignKey('TRPKB.Disease')
    prognosis = models.CharField(max_length=200)
    type_ = models.CharField(max_length=50, null=True, blank=True)
    endpoint = models.CharField(max_length=50, null=True, blank=True)
    original = models.CharField(max_length=10)
    statistical_method = models.CharField(max_length=50, null=True, blank=True)
    software = models.CharField(max_length=50, null=True, blank=True)
    case_meaning = models.CharField(max_length=50, null=True, blank=True)
    control_meaning = models.CharField(max_length=50, null=True, blank=True)
    total_meanning = models.CharField(max_length=50, null=True, blank=True)
    annotation = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{s}".format(self.prognosis)


class Subgourp(models.Model):
    prognosis = models.ForeignKey('TRPKB.Prognosis')
    subgourp = models.CharField(max_length=50)

    def __str__(self):
        return "[{!s}]{s}".format(self.prognosis, self.subgourp)


class Association(models.Model):
    research = models.ForeignKey('TRPKB.Research')
    disease = models.ForeignKey('TRPKB.Disease')
    prognosis = models.ForeignKey('TRPKB.Prognosis')
    subgourp = models.ForeignKey('TRPKB.Subgroup')
    gene = models.ForeignKey('TRPKB.Gene')
    variant = models.ForeignKey('TRPKB.Variant')
    genotype = models.CharField(max_length=50)
    case_number = models.IntegerField(null=True, blank=True)
    control_number = models.IntegerField(null=True, blank=True)
    total_number = models.IntegerField(null=True, blank=True)
    or_u = models.FloatField(null=True, blank=True)
    hr_u = models.FloatField(null=True, blank=True)
    rr_u = models.FloatField(null=True, blank=True)
    ci_u_95 = FloatRangeField(blank=True)
    p_u = models.FloatField(null=True, blank=True)
    or_m = models.FloatField(null=True, blank=True)
    hr_m = models.FloatField(null=True, blank=True)
    rr_m = models.FloatField(null=True, blank=True)
    i_m_95 = FloatRangeField(blank=True)
    p_m = models.FloatField(null=True, blank=True)

    def __str__(self):
        return "[{!s}][{!s}][{!s}]{s}".format(self.disease, self.gene, self.variant, self.genotype)
