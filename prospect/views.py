import sys

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView

from hermes.settings import BETTING
from forms import PlaceBetForm
from models import CTFProfile, Teams, Bet


def faq(request):
    template_args = dict()
    try:
        userprofile = get_object_or_404(CTFProfile, user=request.user)
        template_args['balance'] = userprofile.wallet
    except:
        pass
    return render(request, 'faq.html', template_args)


def about(request):
    template_args = dict()
    try:
        userprofile = get_object_or_404(CTFProfile, user=request.user)
        template_args = dict()
        template_args['balance'] = userprofile.wallet
    except:
        pass
    return render(request, 'about.html', template_args)


@login_required(login_url='/login/')
def index(request):
    return render(request, 'home.html')


@login_required(login_url='/login/')
def view_profile(request, ctfusername):
    template_args = dict()
    userprofile = get_object_or_404(CTFProfile, user=request.user)
    template_args['balance'] = userprofile.wallet

    try:
        user = User.objects.get(username=ctfusername)
        user_profile = get_object_or_404(CTFProfile, user=user)
    except:
        user_profile = 'Not Found'
    template_args['user_profile'] = user_profile

    return render(request, 'viewprofile.html', template_args)


class CTFProfileUpdate(UpdateView):
    fields = ['ctfcount', 'confidence', 'skills', 'training']
    template_name_suffix = '_update_form'

    def get_object(self):
        request = self.request
        return get_object_or_404(CTFProfile, user_id=request.user.id)

    def get_context_data(self, **kwargs):
        context = super(CTFProfileUpdate, self).get_context_data(**kwargs)
        userprofile = get_object_or_404(CTFProfile, user=self.request.user)
        context['balance'] = userprofile.wallet
        return context


@login_required(login_url='/login/')
def updateprofilesuccess(request):
    template_args = dict()
    userprofile = get_object_or_404(CTFProfile, user=request.user)
    template_args['balance'] = userprofile.wallet

    return render(request, 'updateprofilesuccess.html')


@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def ctfadmin(request):
    template_args = dict()
    user = request.user
    user_profile = get_object_or_404(CTFProfile, user=user)
    wallet_balance = user_profile.wallet
    template_args['balance'] = wallet_balance
    template_args['profiles'] = CTFProfile.objects.all().order_by('name')
    template_args['teams'] = Teams.objects.all().order_by('name')

    return render(request, 'ctfadmin.html', template_args)


class AdminCTFProfileUpdate(UpdateView):
    fields = ['ctfcount', 'confidence', 'skills', 'training', 'team']
    model = CTFProfile
    template_name_suffix = '_update_form'
    success_url = '../../ctfadmin/'

    def get_object(self):
        return get_object_or_404(CTFProfile, user_id=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(AdminCTFProfileUpdate, self).get_context_data(**kwargs)
        userprofile = get_object_or_404(CTFProfile, user=self.request.user)
        context['balance'] = userprofile.wallet
        return context


class AdminCTFTeamUpdate(UpdateView):
    fields = ['name', 'slogan', 'user1', 'user2', 'user3']
    model = Teams
    template_name_suffix = '_update_form'
    success_url = '../../ctfadmin'

    def get_object(self):
        return get_object_or_404(Teams, id=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(AdminCTFTeamUpdate, self).get_context_data(**kwargs)
        userprofile = get_object_or_404(CTFProfile, user=self.request.user)
        context['balance'] = userprofile.wallet
        return context


class CTFTeamList(ListView):
    model = Teams

    def get_context_data(self, **kwargs):
        context = super(CTFTeamList, self).get_context_data(**kwargs)
        try:
            userprofile = get_object_or_404(CTFProfile, user=self.request.user)
            context['balance'] = userprofile.wallet
            context['teams_list'] = self.object_list.order_by('odds')
        except:
            context['teams_list'] = self.object_list.order_by('odds')
            pass

        return context


class CTFCreateTeam(CreateView):
    model = Teams
    fields = ['name', 'slogan', 'user1', 'user2', 'user3']
    template_name_suffix = '_create_form'
    success_url = reverse_lazy('ctf-admin')


@login_required(login_url='/login/')
def place_bet(request, teamid):
    template_args = {}
    team = get_object_or_404(Teams, id=teamid)
    template_args['team'] = team
    user = request.user
    user_profile = get_object_or_404(CTFProfile, user=user)

    wallet_balance = user_profile.wallet
    template_args['balance'] = wallet_balance

    bet_form = PlaceBetForm()
    template_args['form'] = bet_form
    template_args['betting'] = BETTING

    if BETTING:
        if request.method == 'POST':
            bet_form = PlaceBetForm(request.POST)
            if bet_form.is_valid():
                try:
                    amount = abs(int(bet_form['amount'].value()))
                except:
                    amount = abs(int(float(bet_form['amount'].value())))
                if amount > wallet_balance:
                    template_args['error'] = 'You don\'t have enough credits (' + str(
                        wallet_balance) + ') to wager that amount'
                    return render(request, 'bet.html', template_args)
                else:
                    user_profile.wallet -= amount
                    user_profile.save(update_fields=['wallet'])
                    Bet.objects.create(user=user, team=team, amount=amount)
                    return HttpResponseRedirect('/listteams/')

    return render(request, 'bet.html', template_args)


def wallet(request):
    template_args = dict()
    user = request.user
    user_profile = get_object_or_404(CTFProfile, user=user)
    wallet_balance = user_profile.wallet
    template_args['balance'] = wallet_balance

    wagers = Bet.objects.filter(user_id=user.id).select_related().values('id', 'team__name',
                                                                         'amount')  # .annotate(total=Sum('amount'))
    template_args['wagers'] = wagers
    wager_list = list()

    for wager in wagers:
        temp_dict = dict()
        temp_dict['team'] = wager['team__name']
        team = Teams.objects.get(name=wager['team__name'])
        odds = team.odds
        amount = wager['amount']
        temp_dict['amount'] = amount
        temp_dict['odds'] = odds
        temp_dict['stand_to_win'] = amount + (amount * odds)
        wager_list.append(temp_dict)

    template_args['wager_list'] = wager_list

    return render(request, 'wallet.html', template_args)


class CTFDeleteTeam(DeleteView):
    model = Teams
    success_url = reverse_lazy('ctf-admin')
    template_name_suffix = '_confirm_delete'

    def get_context_data(self, **kwargs):
        context = super(CTFDeleteTeam, self).get_context_data(**kwargs)

        return context


class UserList(ListView):
    model = User
    template_name = 'propect/user_list.html'

    def get_context_data(self, **kwargs):
        context = super(UserList, self).get_context_data(**kwargs)

        return context


def results(request):
    template_args = {}
    try:
        user = request.user
        user_profile = get_object_or_404(CTFProfile, user=user)
        wallet_balance = user_profile.wallet
        template_args['balance'] = wallet_balance
    except:
        pass

    return render(request, 'results.html', template_args)
