from . import models
from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants, check_and_ok
from django.conf import settings
import time
import random

class holdon(Page):
    def is_displayed(self):
        return self.round_number == 1
    def vars_for_template(self):
        return {
            'debug':settings.DEBUG,
        }


class Init(Page):

    def is_displayed(self):
        return self.round_number == 1
    
    def vars_for_template(self):


        players_per_group = len(self.group.get_players())

        fig1_path = ("hotellingmarketup_00/fig_" + 
        str(self.session.config['players_per_group']) +
        "p/fig1_" +
        str(self.session.config['players_per_group']) +
        "p.jpg")

        fig2_path = ("hotellingmarketup_00/fig_" + 
        str(self.session.config['players_per_group']) +
        "p/fig2_" +
        str(self.session.config['players_per_group']) +
        "p.jpg")

        fig3_path = ("hotellingmarketup_00/fig_" + 
        str(self.session.config['players_per_group']) +
        "p/fig3_" +
        str(self.session.config['players_per_group']) +
        "p.jpg")

        return {
            'fig1_path':fig1_path,
            'fig2_path':fig2_path,
            'fig3_path':fig3_path,
            'debug':settings.DEBUG,
            'players_per_group':players_per_group
        }

class instructions_display(Page):
    pass

page_sequence = [
    holdon,
    Init,
    instructions_display,
    ]






