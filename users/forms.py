from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

crawled_dropdown_choices = []

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class SearchURL(forms.Form):
    url = forms.URLField(label='URL', help_text='Enter seed URL')
    depth_url = forms.IntegerField(label='Depth of search',help_text='Enter number of pages to be crawled (Default: 3)', required=False)
    
class SearchKeyword(forms.Form):
    keyword = forms.CharField(label='Keyword', help_text='Enter keyword')
    depth_key = forms.IntegerField(label='Depth of search',help_text='Enter number of pages to be crawled (Default: 3)', required=False)
    isIterative = forms.BooleanField(label = 'Perform repeated crawling 5 times', required=False)

class SearchKeywordPlt(forms.Form):
    p_choices = [
        (1, 'Instagram'),
        (2, 'Twitter'),
    ]
    keyword = forms.CharField(label='Keyword', help_text='Enter keyword')
    platform = forms.CharField(label='Platform', help_text='Choose platform to crawl on', widget=forms.Select(choices=p_choices))
    depth_key = forms.IntegerField(label='Depth of search',help_text='Enter number of pages to be crawled (Default: 3)', required=False)
    isIterative = forms.BooleanField(label = 'Perform repeated crawling 5 times', required=False)

class CrawlDropdownSelect(forms.Form):
    def __init__(self, crawled_dropdown_choices, *args, **kwargs):
        super(CrawlDropdownSelect, self).__init__(*args, **kwargs)
        self.fields['crawled_choice'] = forms.ChoiceField(label=False, choices=crawled_dropdown_choices, widget=forms.Select(attrs={'onchange': 'form.submit();'}), required=False)

class CustomSimilarityPlatformSelect(forms.Form):
    def __init__(self, platform_choices, *args, **kwargs):
        super(CustomSimilarityPlatformSelect, self).__init__(*args, **kwargs)
        self.fields['platform_choice'] = forms.ChoiceField(label=False, choices=platform_choices, widget=forms.Select(attrs={'onchange': 'form.submit();'}), required=False)

class CustomSimilarityKeywordSelect(forms.Form):
    def __init__(self, visited_keywords_choices, *args, **kwargs):
        super(CustomSimilarityKeywordSelect, self).__init__(*args, **kwargs)
        self.fields['keyword_choice'] = forms.MultipleChoiceField(label=False, choices=visited_keywords_choices, widget=forms.CheckboxSelectMultiple, required=False)