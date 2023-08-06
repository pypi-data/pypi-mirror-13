# ~*~ coding: utf-8 ~*~
from django import forms
from datetimewidget.widgets import DateTimeWidget
from django.utils.translation import ugettext_lazy as _
from django.forms import formset_factory
from django.forms.models import modelformset_factory, inlineformset_factory
from virtenviro.content.models import *

__author__ = 'Kamo Petrosyan'


class PagesAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PagesAdminForm, self).__init__(*args, **kwargs)
        self.fields['parent'].queryset = Page.objects.filter(is_category=True)

    class Meta:
        model = Page
        exclude = ['last_modified']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': _('Title'), 'class': "form-control"}),
            'slug': forms.TextInput(attrs={'placeholder': _('Slug'), 'class': "form-control"}),
            'template': forms.Select(attrs={'class': "form-control"}),
            'parent': forms.Select(attrs={'class': "form-control"}),
            'ordering': forms.NumberInput(attrs={'class': "form-control", 'min': 0}),
            'pub_datetime': DateTimeWidget(attrs={'id': "id_pub_datetime"}, usel10n=True, bootstrap_version=3),
            'last_modified_by': forms.Select(attrs={'disabled': 'disabled', 'class': 'form-control disabled'})
        }

    def clean_parent(self):
        parent = self.cleaned_data.get('parent')

        if not parent:
            parent = None

        return parent


class ContentAdminForm(forms.ModelForm):
    class Meta:
        model = Content
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': _('Title'), 'class': "form-control"}),
            'h1': forms.TextInput(attrs={'placeholder': _('H1'), 'class': "form-control"}),
            'intro': forms.Textarea(attrs={'placeholder': _('Intro text'), 'class': 'form-control', 'rows': 4}),
            'content': forms.Textarea(attrs={'placeholder': _('Intro text'), 'class': 'ckeditor'}),
            'template': forms.Select(attrs={'class': "form-control"}),
            'language': forms.Select(attrs={'class': "form-control disabled"}),
            'meta_title': forms.TextInput(attrs={'placeholder': _('Meta title'), 'class': "form-control"}),
            'meta_keywords': forms.Textarea(attrs={'placeholder': _('Meta keywords'), 'class': 'form-control', 'rows': 2}),
            'meta_description': forms.Textarea(attrs={'placeholder': _('Meta description'), 'class': 'form-control', 'rows': 2}),
            'author': forms.Select(attrs={'class': 'form-control'}),
            'pub_datetime': DateTimeWidget(attrs={'class': 'form-control'}, usel10n=True, bootstrap_version=3),
            'last_modified_by': forms.Select(attrs={'disabled': 'disabled', 'class': 'form-control disabled'})
        }
        exclude = ['parent']

    class Media:
        try:
            if settings.CKEDITOR:
                js = (
                    '/static/ckeditor/ckeditor.js',
                    '/static/filebrowser/js/FB_CKEditor.js',
                    '/static/js/ckeditor.js',
                )
                css = {'all': ('/static/css/ckeditor.css',), }
        except AttributeError:
            pass


ContentAdminFormset = inlineformset_factory(
        Page,
        Content,
        form=ContentAdminForm,
        extra=len(settings.LANGUAGES),
        exclude=['last_modified'])
