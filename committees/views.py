import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.static import serve

from committees.models import Committee, position_paper_upload_path
from committees.forms import AdHocAppForm, BRICSAppForm, NixonAppForm, WallStreetAppForm
from committees.utils import get_committee_from_email


def view(request, slug):
    committee = get_object_or_404(Committee, slug=slug)
    if not committee.is_visible:
        raise Http404

    # If the user is a member of the dais, show a link to the uploads page
    is_dais = get_committee_from_email(request.user.username) == committee

    data = {
        'title': committee.name,
        'is_dais': is_dais,
        'committee': committee,
        'dais_template': 'dais_photos/%s.html' % committee.slug,
        'DAIS_PHOTO_URL': '%simg/dais/%s/' % (settings.STATIC_URL, committee.slug),
    }

    return render(request, 'committee.html', data)


def application(request, slug):
    # Hard-coding the list of committees with applications for now
    # This should really be a field on the committee (for next year)
    committee = get_object_or_404(Committee, slug=slug)

    app_forms = {
        'ad-hoc': AdHocAppForm,
        'brics': BRICSAppForm,
        'frost-nixon': NixonAppForm,
        'wall-street': WallStreetAppForm,
    }

    if slug in app_forms:
        app_form = app_forms[slug]

    if request.method == 'POST':
        form = app_form(request.POST)

        if form.is_valid():
            form.save()

            data = {
                'committee': committee,
                'title': 'Successful application for %s' % committee.name,
            }

            return render(request, 'committee_app_success.html', data)
    else:
        form = app_form

    data = {
        'deadline': 'November 18th',
        'title': 'Application for %s' % committee.name,
        'intro_template': 'committee_apps/%s.md' % slug,
        'committee': committee,
        'form': form,
    }

    return render(request, 'committee_app.html', data)


@login_required
def serve_papers(request, file_name):
    # Check if user is an admin/mod OR if the user uploaded the file OR dais
    is_authorised = False
    full_path = os.path.join(position_paper_upload_path, file_name)

    if request.user.is_staff:
        is_authorised = True
    elif request.user.username.endswith('@mcmun.org'):
        # Check the dais
        committee = get_committee_from_email(request.user.username)
        if committee and committee.committeeassignment_set.filter(position_paper=full_path):
            is_authorised = True
    else:
        user_schools = request.user.registeredschool_set.filter(is_approved=True)
        if user_schools.count() == 1:
            school = user_schools[0]
            if school.committeeassignment_set.filter(position_paper=full_path):
                is_authorised = True

    if is_authorised:
        return serve(request, file_name, os.path.join(settings.MEDIA_ROOT, position_paper_upload_path))
    else:
        raise PermissionDenied


@login_required
def list_papers(request, slug):
    committee = get_object_or_404(Committee, slug=slug)

    # Only the dais for this committee and other admins can access this
    if (get_committee_from_email(request.user.username) == committee
        or request.user.is_staff):
        data = {
            'title': 'Position papers for %s' % committee.name,
            'committee': committee,
            'assignments': committee.committeeassignment_set.order_by('-position_paper'),
        }

        return render(request, 'list_papers.html', data)
    else:
        raise Http404
