# ~*~ coding: utf-8 ~*~
__author__ = 'Kamo Petrosyan'
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.utils.http import urlquote
from django.conf import settings
from virtenviro.content.models import *
from virtenviro.content.admin_forms import *
from virtenviro.utils import paginate

template_str = 'virtenviro/admin/content/{}'


@staff_member_required
def content_page(request):
    template = template_str.format('change_list.html')

    context = {
        'pages': Page.objects.filter(parent__isnull=True),
    }

    return render(request, template, context)


@staff_member_required
def content_page_edit(request, page_id):
    template = template_str.format('page_form.html')
    context = {}

    try:
        page = Page.objects.get(pk=page_id)
        context['current_page'] = page
    except Page.DoesNotExist:
        raise Http404

    initials = []
    content_forms = {}
    for lang in settings.LANGUAGES:
        if page.get_content(language=lang) is None:
            initials.append({'language': lang[0], 'author': request.user})

    if request.method == 'POST':
        page_form = PagesAdminForm(request.POST, instance=page, prefix='page')
        for lang in settings.LANGUAGES:
            try:
                content = page.contents.get(language=lang[0])
                content_forms[lang[0]] = ContentAdminForm(request.POST, instance=content,
                                                          prefix='content_{}'.format(lang[0]))
            except Content.DoesNotExist:
                content_forms[lang[0]] = ContentAdminForm(request.POST, initial={'language': lang[0]},
                                                          prefix='content_{}'.format(lang[0]))

        if page_form.is_valid():
            is_valid = True
            page = page_form.save()
            for lang in settings.LANGUAGES:
                if content_forms[lang[0]].has_changed() and content_forms[lang[0]].is_valid():
                    content_forms[lang[0]].save()
                else:
                    is_valid = False
    else:
        page_form = PagesAdminForm(instance=page, prefix='page')
        for lang in settings.LANGUAGES:
            try:
                content = page.contents.get(language=lang[0])
                content_forms[lang[0]] = ContentAdminForm(instance=content,
                                                          prefix='content_{}'.format(lang[0]))
            except Content.DoesNotExist:
                content_forms[lang[0]] = ContentAdminForm(initial={'language': lang[0]},
                                                          prefix='content_{}'.format(lang[0]))

    context['page'] = page
    context['pages'] = Page.objects.all()
    context['page_form'] = page_form
    context['content_forms'] = content_forms

    return render(request, template, context)


@staff_member_required
def content_page_add(request):
    template = template_str.format('page_form.html')
    context = {}

    initials = []
    content_forms = {}
    for lang in settings.LANGUAGES:
        initials.append({'language': lang[0], 'author': request.user})

    if request.method == 'POST':
        page_form = PagesAdminForm(request.POST)
        for lang in settings.LANGUAGES:
            content_forms[lang[0]] = ContentAdminForm(request.POST, initial={'language': lang[0]},
                                                      prefix='content_{}'.format(lang[0]))

        if page_form.is_valid():
            is_valid = True
            page = page_form.save()
            for lang in settings.LANGUAGES:
                if content_forms[lang[0]].has_changed() and content_forms[lang[0]].is_valid():
                    content_forms[lang[0]].save()
                else:
                    is_valid = False
            return redirect('vadmin:content_page_edit', page.pk)
    else:
        page_form = PagesAdminForm()
        for lang in settings.LANGUAGES:
            content_forms[lang[0]] = ContentAdminForm(initial={'language': lang[0]},
                                                      prefix='content_{}'.format(lang[0]))

    context['pages'] = Page.objects.all()
    context['page_form'] = page_form
    context['content_forms'] = content_forms

    return render(request, template, context)

