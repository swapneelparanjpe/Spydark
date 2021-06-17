from django import forms

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
        self.fields['link_choice'] = forms.ChoiceField(label=False, choices=link_choices, widget=forms.Select, required=False)

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
