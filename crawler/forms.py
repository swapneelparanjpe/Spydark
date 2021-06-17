from django import forms

class SearchURL(forms.Form):
    url = forms.URLField(label='URL', help_text='Enter seed URL')
    depth_url = forms.IntegerField(label='Depth of search',help_text='Enter number of pages to be crawled (Default: 3)', required=False)
    
class SearchKeyword(forms.Form):
    keyword = forms.CharField(label='Keyword', help_text='Enter keyword')
    depth_key = forms.IntegerField(label='Depth of search',help_text='Enter number of pages to be crawled (Default: 3)', required=False)
    isIterative = forms.BooleanField(label = 'Perform repeated crawling 5 times', required=False)

class SearchKeywordPlt(forms.Form):
    p_choices = [
        (1, 'Google'),
        (2, 'Instagram'),
        (3, 'Twitter'),
    ]
    keyword = forms.CharField(label='Keyword', help_text='Enter keyword')
    platform = forms.CharField(label='Platform', help_text='Choose platform to crawl on', widget=forms.Select(choices=p_choices))
    depth_key = forms.IntegerField(label='Depth of search',help_text='Enter number of pages to be crawled (Default: 3)', required=False)
    isIterative = forms.BooleanField(label = 'Perform repeated crawling 5 times', required=False)

