from committees.models import AdHocApplication, EnronApplication, \
     CriminalCourtApplication, NcaaApplication, NintendoApplication, \
     CommitteeAssignment, DelegateAssignment, AwardAssignment

from django import forms


class AdHocAppForm(forms.ModelForm):
    class Meta:
        model = AdHocApplication


class EnronAppForm(forms.ModelForm):
    class Meta:
        model = EnronApplication


class CriminalCourtAppForm(forms.ModelForm):
    class Meta:
        model = CriminalCourtApplication


class NcaaAppForm(forms.ModelForm):
    class Meta:
        model = NcaaApplication


class NintendoAppForm(forms.ModelForm):
    class Meta:
        model = NintendoApplication


AwardAssignmentFormset = forms.models.modelformset_factory(AwardAssignment,
    fields=('position',), extra=0)


CommitteeAssignmentFormset = forms.models.modelformset_factory(
    CommitteeAssignment, fields=('position_paper',), extra=0)

DelegateAssignmentFormset = forms.models.modelformset_factory(
    DelegateAssignment, fields=('delegate_name',), extra=0)
