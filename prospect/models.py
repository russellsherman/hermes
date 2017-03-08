from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save
from django.utils.encoding import python_2_unicode_compatible
from django.shortcuts import get_object_or_404
from datetime import datetime

# Create your models here.


@python_2_unicode_compatible
class Teams(models.Model):
    name = models.CharField(max_length=256)
    slogan = models.CharField(max_length=2048, null=True, blank=True, default='')
    user1 = models.CharField(max_length=100, null=True, blank=True, default='')
    user2 = models.CharField(max_length=100, null=True, blank=True, default='')
    user3 = models.CharField(max_length=100, null=True, blank=True, default='')
    odds = models.FloatField(default=-1.0)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class CTFProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Teams, default=False, on_delete=models.CASCADE)
    ctfcount = models.IntegerField(null=True, verbose_name="CTF Count History", help_text='How many CTFs have you participated in?')
    confidence = models.CharField(max_length=2048, verbose_name="Confidence Level", null=True, help_text='How confident are you that you will win?')
    skills = models.CharField(max_length=2048, verbose_name="Skills", null=True, help_text='What skills can you bring to your team?')
    training = models.CharField(max_length=2048, verbose_name="Training Taken", null=True, help_text='What types of training have you taken?')
    wallet = models.IntegerField(default=100)

    def get_absolute_url(self):
        return reverse('updateprofile')

    def __str__(self):
        return "%s" % self.user


class Bet(models.Model):
    createdtm = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField(verbose_name='Amount')
    user = models.ForeignKey(User)
    team = models.ForeignKey(Teams)

    def __str__(self):
        return self.team


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        CTFProfile.objects.get_or_create(user=instance)


def update_odds(sender, instance, created, **kwargs):
    if created:
        total_bets = float(Bet.objects.all().aggregate(models.Sum('amount'))['amount__sum'])
        all_teams = Teams.objects.all()
        for team in all_teams:
            try:
                total_team_bets = float(Bet.objects.filter(team=team).aggregate(models.Sum('amount'))['amount__sum'])
                team.odds = (total_bets - total_team_bets) / total_team_bets
                team.save(update_fields=['odds'])
            except:
                pass


post_save.connect(create_user_profile, sender=User)
post_save.connect(update_odds, sender=Bet)
