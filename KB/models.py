from django.db import models
from django.contrib.postgres.fields import ArrayField, IntegerRangeField, FloatRangeField


class Tumor(models.Model):
    name = models.CharField(max_length=50, unique=True)
    mesh_term = models.CharField(max_length=50, unique=True, null=True, blank=True)
    mesh_id = models.IntegerField(unique=True, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.disease)


class Gene(models.Model):
    gene_official_symbol = models.CharField(max_length=50, unique=True)
    entrez_gene_id = models.IntegerField(unique=True, null=True, blank=True)
    gene_alternative_symbols = ArrayField(models.CharField(max_length=50), blank=True)
    gene_official_full_name = models.CharField(max_length=100, null=True, blank=True)
    gene_official_full_name = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.gene_official_symbol)


class Variant(models.Model):
    gene = models.ForeignKey('KB.Gene')
    variant_dbsnp = models.CharField(max_length=200)
    hgvs_g = models.CharField(max_length=50)
    hgvs_p = models.CharField(max_length=50)

    def __str__(self):
        return "[{!s}]{}".format(self.gene, self.variant_dbsnp)


class Treatment(models.Model):
    treatment_type = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return "{}".format(self.treatment_type)


class EvidenceBasedMedicineLevel(models.Model):
    ebml = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return "{}".format(self.ebml)


class Research(models.Model):
    title = models.CharField(max_length=500, unique=True)
    language = models.CharField(max_length=50, null=True, blank=True)
    pub_year = models.IntegerField(null=True, blank=True)
    pubmed_id = models.IntegerField(null=True, blank=True)
    url = models.UrlField(null=True, blank=True)
    pub_type = models.CharField(max_length=50, null=True, blank=True)
    ebml = models.ForeignKey('KB.EvidenceBasedMedicineLevel', null=True, blank=True)
    ethnicity = models.CharField(max_length=50, null=True, blank=True)
    patient_number = models.IntegerField(null=True, blank=True)
    male = models.IntegerField(null=True, blank=True)
    female = models.IntegerField(null=True, blank=True)
    median_age = models.FloatField(null=True, blank=True)
    mean_age = models.FloatField(null=True, blank=True)
    age_range = IntegerRangeField(blank=True)
    treatment_desc = models.TextField(null=True, blank=True)
    treatment_type = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return "{}".format(self.title)


class Prognosis(models.Model):
    prognosis = models.CharField(max_length=200)
    prognosis_type = models.CharField(max_length=50, null=True, blank=True)
    endpoint = models.CharField(max_length=50, null=True, blank=True)
    original = models.CharField(max_length=10)
    case_meaning = models.CharField(max_length=50, null=True, blank=True)
    control_meaning = models.CharField(max_length=50, null=True, blank=True)
    total_meanning = models.CharField(max_length=50, null=True, blank=True)
    annotation = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.prognosis)


class Subgroup(models.Model):
    prognosis = models.ForeignKey('KB.Prognosis')
    subgourp = models.CharField(max_length=50)

    def __str__(self):
        return "[{!s}]{}".format(self.prognosis, self.subgourp)


class Association(models.Model):
    research = models.ForeignKey('KB.Research')
    tumor = models.ForeignKey('KB.Tumor')
    variant = models.ForeignKey('KB.Variant')
    prognosis = models.ForeignKey('KB.Prognosis')
    subgourp = models.ForeignKey('KB.Subgroup', null=True, blank=True)
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
        return "[{!s}][{}][{}]{}".format(self.tumor, self.variant.gene.gene_official_symbol,
                                         self.variant.variant_dbsnp, self.genotype)
