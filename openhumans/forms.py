from django import forms


class FileUploadForm(forms.Form):
    file_desc = forms.CharField(label='File Description', max_length=100)
    file_tags = forms.CharField(label='Tags for your data',
                                widget=forms.TextInput(attrs={'placeholder': 'comma separated values'}))
    data_file = forms.FileField(label='File to upload')

    def get_tags(self):
        return self.data['file_tags']

    def get_file(self):
        return self.files['data_file']

    def get_description(self):
        return self.data['file_desc']
