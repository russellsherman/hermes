"""hermes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required

from prospect.models import CTFProfile, Teams
from prospect import views as prospect

urlpatterns = [
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^$', prospect.faq, name='home'),

    # Basic FAQ (Anonymous OK)
    url(r'^faq/$', prospect.faq, name='faq'),

    # About Page (Anonymous OK)
    url(r'^about/$', prospect.about, name='about'),

    # Results Page
    url(r'^results/$', prospect.results, name='results'),
    url(r'^updateprofile/$', login_required(prospect.CTFProfileUpdate.as_view(model=CTFProfile)),
        name='updateprofile'),

    # View a singe profile
    url(r'^viewprofile/(?P<ctfusername>.*)/$', prospect.view_profile, name='view-profile'),
    url(r'^updateprofilesuccess/$', login_required(prospect.updateprofilesuccess), name='updateprofilesuccess'),
    url(r'^listteams/$', prospect.CTFTeamList.as_view(), name='list-teams'),
    url(r'^placebet/(?P<teamid>[0-9]{0,4})/$', login_required(prospect.place_bet), name='place-bet'),
    url(r'^wallet/$', login_required(prospect.wallet), name='wallet'),

    # Admin functionality
    # Manage users
    url(r'^ctfadmin/$', prospect.ctfadmin, name='ctf-admin'),
    url(r'^listusers/$', staff_member_required(prospect.UserList.as_view(), login_url='/faq/'), name='list-users'),
    url(r'^addteam/$', staff_member_required(prospect.CTFCreateTeam.as_view(success_url='/ctfadmin/'), login_url='/faq/'), name='create-team'),
    url(r'^deleteteam/(?P<pk>[0-9]{0,4})/$', staff_member_required(prospect.CTFDeleteTeam.as_view(), login_url='/faq/'), name='delete-team'),
    url(r'^adminupdateprofile/(?P<slug>[0-9]{0,4})/$', staff_member_required(prospect.AdminCTFProfileUpdate.as_view(model=CTFProfile), login_url='/faq/'),
        name='adminupdateprofile'),
    url(r'^adminupdateteam/(?P<slug>[0-9]{0,4})/$', staff_member_required(prospect.AdminCTFTeamUpdate.as_view(model=Teams), login_url='/faq/'),
        name='adminupdateteam'),

    url(r'^health-check', prospect.health_check, name='health-check')
]

