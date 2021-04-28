# -*- coding: utf-8 -*-
# <standard imports>
from __future__ import division

import otree.models
from otree.db import models
from otree import widgets
from otree.common import Currency as c, currency_range, safe_json
from otree.constants import BaseConstants
from otree.models import BaseSubsession, BaseGroup, BasePlayer

from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random
# </standard imports>

author = 'Curtis Kephart'

doc = """
simple intro app. for instructions. 
"""

def check_and_ok(user_total, reference_ints):
    ok = (user_total == sum(reference_ints))
    return ok

class Constants(BaseConstants):
    name_in_url = 'end'
    num_rounds = 1
    players_per_group = None
    transport_cost = 1

class Subsession(BaseSubsession):

    def before_session_starts(self):
        
        numberOfPeriods = len(self.session.config['t'])
        paidPeriod = x = random.randint(1, numberOfPeriods)
        for p in self.get_players():
            p.paidPeriod = paidPeriod



class Group(BaseGroup):
	pass



class Player(BasePlayer):
    
    paidPeriod = models.PositiveIntegerField(
        doc="""The length of the real effort task timer."""
    )
