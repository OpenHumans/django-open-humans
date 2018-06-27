from django import forms


class DeleteDataFileForm(forms.Form):
    """
    A form for validating the deletion of files for a project.
    """

    file_id = forms.IntegerField(
        required=False,
        label='File ID')

    file_basename = forms.CharField(
        required=False,
        label='File basename')

    all_files = forms.BooleanField(
        required=False,
        label='All files')
