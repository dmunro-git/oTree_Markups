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
2-player Hotelling location and price game. Locations fixed, and prices adjusted in by players. 
"""

class Constants(BaseConstants):
    name_in_url = 'task'
    task_timer = 5 #see Subsession, before_session_starts setting. 
    num_rounds = 350 # NEEDS TO BE Periods (15) * (subperiods-per-period (20) + extras (2)
    players_per_group = None
    transport_cost = 0.1

class Subsession(BaseSubsession):

	def creating_session(self):

		players = self.get_players()
		players_per_group = self.session.config['players_per_group']
		numSubperiods = self.session.config['numSubperiods']

		# Each period has:
		# - one round zero to initiate prices
		# - numSubperiods rounds
		# - one extra round for summary
		# so if there are 20 subperiods, you should see 22-rounds for each period
		# all this is reflect in the "elif" below
		for p in self.get_players():
			# set Period and SubPeriod Numbers
			if self.round_number == 1:
				p.period_number = 1
				p.subperiod_number = 0
			elif (((self.round_number - 1) / (numSubperiods + 2)) % 1 != 0):
				#if still within period defined by numSubperiods;
				p.period_number = p.in_round(self.round_number - 1).period_number
				p.subperiod_number = p.in_round(self.round_number - 1).subperiod_number + 1
			else: 
				#tick period up one
				p.period_number = p.in_round(self.round_number - 1).period_number + 1
				p.subperiod_number = 0


		#### GROUPING #########################
		# grouping handled in two places, 
		# below, and in the in self.get_players() control structure
		# - Set Groups based on Period Numbers. 
		# - but randomize between periods
		self.group_randomly()
		group_matrix = []
		for i in range(0, len(players), players_per_group):
			group_matrix.append(players[i:i+players_per_group])
		self.set_group_matrix(group_matrix)


		for p in self.get_players():

			########################	
			# configure t, mc and rp
			########################

			# Set shopping costs / transport costs
			periodIndex = (p.period_number - 1)
			if p.period_number <= len(self.session.config['t']):  #if period exits
				if p.subperiod_number == 0: # if initial subperiod, just set to subpeeriod 1
					subperiodIndex = (p.subperiod_number % len(self.session.config['t'][periodIndex]))
					p.transport_cost = self.session.config['t'][periodIndex][0]
				elif p.subperiod_number == (numSubperiods + 1):
					p.transport_cost = None
				else:
					subperiodIndex = (p.subperiod_number % len(self.session.config['t'][periodIndex]))
					p.transport_cost = self.session.config['t'][periodIndex][subperiodIndex - 1]


			# set mill costs, marginal cost to firm. 
			if p.period_number <= len(self.session.config['mc']):
				if p.subperiod_number == 0: # if initial subperiod. 
					subperiodIndex = (p.subperiod_number % len(self.session.config['mc'][periodIndex]))
					p.mc = self.session.config['mc'][periodIndex][0]
				elif p.subperiod_number == (numSubperiods + 1):
					p.mc = None
				else: 
					subperiodIndex = (p.subperiod_number % len(self.session.config['mc'][periodIndex]))
					p.mc = self.session.config['mc'][periodIndex][subperiodIndex - 1]

			# set reservation prices, max price consumer willing to pay
			if p.period_number <= len(self.session.config['rp']): #if period exists
				if p.subperiod_number == 0: # if initial subperiod. 
					subperiodIndex = (p.subperiod_number % len(self.session.config['rp'][periodIndex]))
					p.rp = self.session.config['rp'][periodIndex][0]
				elif p.subperiod_number == (numSubperiods + 1):
					p.rp = None
				else:
					subperiodIndex = (p.subperiod_number % len(self.session.config['rp'][periodIndex]))
					p.rp = self.session.config['rp'][periodIndex][subperiodIndex - 1]


			p.subperiod_time = self.session.config['subperiod_time']

			# Grouping part 2
			# also get price
			if p.period_number <= len(self.session.config['t']):
				if self.round_number == 1: #first round
					self.group_randomly()
					p.price = random.uniform(0, 1)
				elif (((self.round_number - 1) /  (numSubperiods + 2)) % 1 == 0):
					self.group_randomly()
					p.price = random.uniform(0, 1)
				else:
					self.group_like_round(self.round_number - 1)


		# set locations 
		# - since loc depend on group, and id within group, 
		#   this must occur after groups are set
		for p in self.get_players():

			if p.period_number <= len(self.session.config['t']):
				#set loc based on player id
				p.loc = p.participant.vars["loc"] = ((1 / players_per_group)/2) + ((p.id_in_group - 1) * (1 / players_per_group)) 





class Group(BaseGroup):
	pass


class Player(BasePlayer):







	subperiod_time = models.PositiveIntegerField(
	    doc="""The length of the real effort task timer."""
	)

	period_number = models.PositiveIntegerField(
		doc='''period number'''
	)

	subperiod_number = models.PositiveIntegerField(
		doc='''subperiod number'''
	)

	rp = models.FloatField(
		doc='''customer reserve price''')

	mc = models.FloatField(
		doc='''firm mill cost''')

	transport_cost = models.FloatField(
	    doc="""transport, or shopping cost"""
	)

	loc = models.FloatField(
		doc="player's location")

	price = models.FloatField(
		doc="player's price in previous round/subperiod")

	next_subperiod_price = models.FloatField(
		doc="player's price in current round/subperiod")
	
	boundary_lo = models.FloatField(
		doc="player's low end of boundary")

	boundary_hi = models.FloatField(
		doc="player's high end of boundary")

	prev_round_payoff = models.FloatField(
		doc="player's payoffs this previous round/subperiod")

	prev_round_cumulative_payoff = models.FloatField(
		doc="player's payoffs cumulative the previous round/subperiod.")



	paid_period = models.IntegerField(
		doc='''1 if this is a paid period, 0 otherwise''')





