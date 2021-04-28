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
    name_in_url = 'task_2p'
    task_timer = 5 #see Subsession, before_session_starts setting. 
    num_rounds = 300
    players_per_group = 2
    transport_cost = 0.1

class Subsession(BaseSubsession):

	def before_session_starts(self):

		numSubperiods = self.session.config['numSubperiods']

		for p in self.get_players():

			# sep Period Numbers
			if self.round_number == 1:
				p.period_number = 1
				p.subperiod_number = 0
			elif (((self.round_number - 1) / (numSubperiods + 1)) % 1 != 0):
				p.period_number = p.in_round(self.round_number - 1).period_number
				p.subperiod_number = p.in_round(self.round_number - 1).subperiod_number + 1
			else: 
				p.period_number = p.in_round(self.round_number - 1).period_number + 1
				p.subperiod_number = 0

			# configure t, mc and rp

			# if initial subperiod. 
			if p.subperiod_number == 0:
				periodIndex = (p.period_number - 1)
				p.transport_cost = self.session.config['t'][periodIndex][0]
				p.mc = self.session.config['mc'][periodIndex][0]
				p.rp = self.session.config['rp'][periodIndex][0]

			else: 
				if p.period_number <= len(self.session.config['t']):
					periodIndex = (p.period_number - 1)
					subperiodIndex = (p.subperiod_number % len(self.session.config['t'][periodIndex]))
					p.transport_cost = self.session.config['t'][periodIndex][subperiodIndex - 1]


				if p.period_number <= len(self.session.config['mc']):
					periodIndex = (p.period_number - 1)
					subperiodIndex = (p.subperiod_number % len(self.session.config['mc'][periodIndex]))
					p.mc = self.session.config['mc'][periodIndex][subperiodIndex - 1]


				if p.period_number <= len(self.session.config['rp']):
					periodIndex = (p.period_number - 1)
					subperiodIndex = (p.subperiod_number % len(self.session.config['rp'][periodIndex]))
					p.rp = self.session.config['rp'][periodIndex][subperiodIndex - 1]

			p.subperiod_time = self.session.config['subperiod_time']

			# Grouping
			if p.period_number <= len(self.session.config['t']):
				if self.round_number == 1:
					self.group_randomly()
					p.price = random.uniform(0, 1)
				elif (((self.round_number - 1) /  (numSubperiods + 1)) % 1 == 0):
					self.group_randomly()
					p.price = random.uniform(0, 1)
				else:
					self.group_like_round(self.round_number - 1)


		for p in self.get_players():

			if p.period_number <= len(self.session.config['t']):
				#set loc based on player id
				p.loc = p.participant.vars["loc"] = ((1 / Constants.players_per_group)/2) + ((p.id_in_group - 1) * (1 / Constants.players_per_group)) 

	




class Group(BaseGroup):

	def set_payoffs(self):
		"""calculate payoffs in round"""

		for p in self.get_players():

			# if no price (ie price-slider unoved), get prev subperiod price
			if p.price == None:
				p.price = p.in_round(self.round_number-1).price

			# variable setup
			if p.id_in_group == 1:
				p1_l = p.loc
				p1_p = p.price
			elif p.id_in_group == 2:
				p2_l = p.loc
				p2_p = p.price
			elif p.id_in_group == 3:
				p3_l = p.loc
				p3_p = p.price
			elif p.id_in_group == 4:
				p4_l = p.loc
				p4_p = p.price

			t = p.transport_cost



		# //p1 - priced out of market
		intersection_1_2 = (t * p2_l+p2_p + t * p1_l - p1_p) / (2*t)
		intersection_1_3 = (t * p3_l+p3_p + t * p1_l - p1_p) / (2*t)
		intersection_1_4 = (t * p4_l+p4_p + t * p1_l - p1_p) / (2*t)

		if ((intersection_1_2 < p1_l) | (intersection_1_3 < p1_l) | (intersection_1_4 < p1_l)):
			p1_boundary_lo = 0 
			p1_boundary_hi = 0 

		# //p4 - priced out of market
		intersection_1_4 = (t *p4_l+p4_p + t * p1_l - p1_p) / (2*t)
		intersection_2_4 = (t *p4_l+p4_p + t * p2_l - p2_p) / (2*t)
		intersection_3_4 = (t *p4_l+p4_p + t * p3_l - p3_p) / (2*t)

		if ((intersection_3_4 > p4_l) | (intersection_2_4 > p4_l) | (intersection_1_4 > p4_l)):
			p4_boundary_lo = 0 
			p4_boundary_hi = 0 

		# //p2 - priced out of market
		intersection_1_2 = (t *p2_l+p2_p + t * p1_l - p1_p) / (2*t)
		intersection_2_3 = (t *p3_l+p3_p + t * p2_l - p2_p) / (2*t)
		intersection_2_4 = (t *p4_l+p4_p + t * p2_l - p2_p) / (2*t)

		if ((intersection_1_2 > p2_l) | (intersection_2_3 < p2_l) | (intersection_2_4 < p2_l)):
			p2_boundary_lo = 0 
			p2_boundary_hi = 0

		# //p3 - priced out of market
		intersection_1_3 = (t *p3_l+p3_p + t * p1_l - p1_p) / (2*t)
		intersection_2_3 = (t *p3_l+p3_p + t * p2_l - p2_p) / (2*t)
		intersection_3_4 = (t *p4_l+p4_p + t * p3_l - p3_p) / (2*t)

		if ((intersection_1_3 > p3_l) | (intersection_2_3 > p3_l) | (intersection_3_4 < p3_l)):
			p3_boundary_lo = 0 
			p3_boundary_hi = 0 



		# //p1
		if ((intersection_1_2 < p1_l) | (intersection_1_3 < p1_l) | (intersection_1_4 < p1_l)):
			p1_boundary_lo = 0 
			p1_boundary_hi = 0 
		elif (intersection_1_2 > p2_l):
			if (intersection_1_3 > p3_l):
				if (intersection_1_4 > p4_l): #//prices below all else
					p1_boundary_lo = 0 
					p1_boundary_hi = 1 
				else:
					p1_boundary_lo = 0 
					p1_boundary_hi = intersection_1_4
			elif (intersection_1_4 < intersection_1_3): # // if p4 priced out p3!
				p1_boundary_lo = 0 
				p1_boundary_hi = intersection_1_4 
			else:
				p1_boundary_lo = 0 
				p1_boundary_hi = intersection_1_3 
		elif ((intersection_1_4 < intersection_1_3) & (intersection_1_4 < intersection_1_2)):
				p1_boundary_lo = 0 
				p1_boundary_hi = intersection_1_4 
		elif (intersection_1_3 < intersection_1_2):
				p1_boundary_lo = 0 
				p1_boundary_hi = intersection_1_3 
		else:
			p1_boundary_lo = 0 
			p1_boundary_hi = intersection_1_2


		# //p4
		if ((intersection_3_4 > p4_l) | (intersection_2_4 > p4_l) | (intersection_1_4 > p4_l)):
			p4_boundary_lo = 0 
			p4_boundary_hi = 0 
		elif (intersection_3_4 < p3_l):
			if (intersection_2_4 < p2_l):
				if (intersection_1_4 < p1_l): #//prices below all else
					p4_boundary_lo = 0 
					p4_boundary_hi = 1 
				else:
					p4_boundary_lo = intersection_1_4 
					p4_boundary_hi = 1 
			elif (intersection_1_4 > intersection_2_4): #// if p4 priced out p3!
					p4_boundary_lo = intersection_1_4 
					p4_boundary_hi = 1 
			else:
				p4_boundary_lo = intersection_2_4 
				p4_boundary_hi = 1
		elif ((intersection_1_4 > intersection_2_4) & (intersection_1_4 > intersection_3_4)):
				p4_boundary_lo = intersection_1_4 
				p4_boundary_hi = 1 
		elif (intersection_2_4 > intersection_3_4):
				p4_boundary_lo = intersection_2_4 
				p4_boundary_hi = 1 
		else:
			p4_boundary_lo = intersection_3_4 
			p4_boundary_hi = 1 


		# //p2
		intersection_1_2 = (t *p2_l+p2_p + t * p1_l - p1_p) / (2*t)
		intersection_2_3 = (t *p3_l+p3_p + t * p2_l - p2_p) / (2*t)
		intersection_2_4 = (t *p4_l+p4_p + t * p2_l - p2_p) / (2*t)

		if ((intersection_1_2 > p2_l) | (intersection_2_3 < p2_l) | (intersection_2_4 < p2_l)):
			p2_boundary_lo = 0 
			p2_boundary_hi = 0 
		else:
			# //p2 left side
			if (intersection_1_2 >= p1_l):
				p2_boundary_lo = intersection_1_2
			elif (intersection_1_2 < p1_l):
				p2_boundary_lo = 0

			# p2 right side
			if (intersection_2_3 > p3_l):
				if (intersection_2_4 > p4_l):
					p2_boundary_hi = 1
				else:
					p2_boundary_hi = intersection_2_4
			elif (intersection_2_4 < intersection_2_3):
				p2_boundary_hi = intersection_2_4
			else:
				p2_boundary_hi = intersection_2_3


		# //p3
		intersection_1_3 = (t *p3_l+p3_p + t * p1_l - p1_p) / (2*t)
		intersection_2_3 = (t *p3_l+p3_p + t * p2_l - p2_p) / (2*t)
		intersection_3_4 = (t *p4_l+p4_p + t * p3_l - p3_p) / (2*t)

		if ((intersection_1_3 > p3_l) | (intersection_2_3 > p3_l) | (intersection_3_4 < p3_l)):
			p3_boundary_lo = 0 
			p3_boundary_hi = 0 
		else:
			# //p3 left side
			if (intersection_2_3 < p2_l):
				if (intersection_1_3 < p1_l):
					p3_boundary_lo = 0
				else:
					p3_boundary_lo = intersection_1_3
			elif (intersection_1_3 > intersection_2_3):
				p3_boundary_lo = intersection_1_3
			else:
				p3_boundary_lo = intersection_2_3

			# // p3 right side
			if (intersection_3_4 <= p4_l):
				p3_boundary_hi = intersection_3_4
			elif (intersection_3_4 > p4_l):
				p3_boundary_hi = 1


		for p in self.get_players():

			# variable setup
			if p.id_in_group == 1:
				p.boundary_lo = p1_boundary_lo
				p.boundary_hi = p1_boundary_hi
			elif p.id_in_group == 2:
				p.boundary_lo = p2_boundary_lo
				p.boundary_hi = p2_boundary_hi
			elif p.id_in_group == 3:
				p.boundary_lo = p3_boundary_lo
				p.boundary_hi = p3_boundary_hi
			elif p.id_in_group == 4:
				p.boundary_lo = p4_boundary_lo
				p.boundary_hi = p4_boundary_hi
				
			p.market_share = p.boundary_hi - p.boundary_lo
			p.round_payoff = p.market_share * p.price
			p.period_num = p.round_number
			p.cumulative_round_payoff = sum([ply.round_payoff / Constants.num_rounds for ply in p.in_all_rounds() if (ply.round_payoff != None)])




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

	transport_cost = models.FloatField(
	    doc="""transport, or shopping cost"""
	)

	mc = models.FloatField(
		doc='''firm mill cost''')

	rp = models.FloatField(
		doc='''customer reserve price''')




	loc = models.FloatField(
		doc="player's location")

	price = models.FloatField(
		doc="player's price in previous round/subperiod")


	boundary_lo = models.FloatField(
		doc="player's low end of boundary")

	boundary_hi = models.FloatField(
		doc="player's high end of boundary")

	round_payoff = models.FloatField(
		doc="player's payoffs this round/subperiod")

	cumulative_round_payoff = models.FloatField(
		doc="player's payoffs sumulative this round/subperiod. Final round's cumulative_round_payoff is score for this period")

	next_subperiod_price = models.FloatField(
		doc="player's price in current round/subperiod")

	paid_period = models.IntegerField(
		doc='''1 if this is a paid period, 0 otherwise''')





