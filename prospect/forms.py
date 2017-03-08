from django import forms
from models import Bet, Teams, User, CTFProfile


class PlaceBetForm(forms.Form):
    amount = forms.IntegerField()

