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

class SimilarityPlatformSelect(forms.Form):
    def __init__(self, platform_choices, *args, **kwargs):
        super(SimilarityPlatformSelect, self).__init__(*args, **kwargs)
        self.fields['platform_choice'] = forms.ChoiceField(label=False, choices=platform_choices, widget=forms.Select(attrs={'onchange': 'form.submit();'}), required=False)

class LinkSimilarityKeywordSelect(forms.Form):
    def __init__(self, visited_keywords_choices, *args, **kwargs):
        super(LinkSimilarityKeywordSelect, self).__init__(*args, **kwargs)
        self.fields['keyword_choice'] = forms.MultipleChoiceField(label=False, choices=visited_keywords_choices, widget=forms.CheckboxSelectMultiple, required=False)

class ContentSimilarityKeywordSelect(forms.Form):
    def __init__(self, keyword_choices, *args, **kwargs):
        super(ContentSimilarityKeywordSelect, self).__init__(*args, **kwargs)
        self.fields['keyword_choice'] = forms.ChoiceField(label=False, choices=keyword_choices, widget=forms.Select(attrs={'onchange': 'form.submit();'}), required=False)

class ContentSimilarityLinkSelect(forms.Form):
    def __init__(self, link_choices, *args, **kwargs):
        super(ContentSimilarityLinkSelect, self).__init__(*args, **kwargs)
        self.fields['link_choice'] = forms.ChoiceField(label=False, choices=link_choices, widget=forms.Select(attrs={'onchange': 'form.submit();'}), required=False)

class ContentSimilarityCustomLink(forms.Form):
    custom_link = forms.URLField(label=False, required=False)


class FlagLinksToTrack(forms.Form):
    def __init__(self, links, *args, **kwargs):
        super(FlagLinksToTrack, self).__init__(*args, **kwargs)
        self.fields['links'] = forms.MultipleChoiceField(label=False, choices=links, widget=forms.CheckboxSelectMultiple, required=False)

class LinkActivityPeriod(forms.Form):
    def __init__(self, flagged_link_choices, *args, **kwargs):
        super(LinkActivityPeriod, self).__init__(*args, **kwargs)
        self.fields['flagged_link_choices'] = forms.ChoiceField(label=False, choices=flagged_link_choices, widget=forms.Select(attrs={'onchange': 'form.submit();'}), required=False)
