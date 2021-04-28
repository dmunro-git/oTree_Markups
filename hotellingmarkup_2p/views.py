from . import models
from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants
from django.conf import settings
import time

class period_init_wait(Page):
    # timeout_seconds = 5

    form_model = models.Player

    def after_all_players_arrive(self):
        pass

    def is_displayed(self):

        if self.round_number == 1:
            self.participant.vars['start_time'] = None

        return self.round_number == 1

    def vars_for_template(self):

        players = []
        for op in self.group.get_players():
            players.append({'id':op.id_in_group,'loc':op.loc, 'price':op.price})
        
        return {
            'players':players,
            'test_p1_l':players[0]['loc'],
            'round':self.round_number,
            'my_loc':self.participant.vars["loc"],
            'treatment_t':self.player.transport_cost,
            'debug':settings.DEBUG,
            'paid_period':self.player.paid_period,
        }

class WaitPage1(WaitPage):

    def after_all_players_arrive(self):
        #calc payoffs and stuff
        # self.group.set_payoffs()
        pass 
    
    def is_displayed(self):
        return self.player.subperiod_number == 1




class task(Page):   
    # timeout_seconds = 10
    # timeout_submission = {'price': 1}

    form_model = models.Player
    form_fields = [
        'next_subperiod_price','round_payoff','boundary_lo','boundary_hi'
        ]
  
  
    def is_displayed(self):
        return ((self.round_number == 0) | ((self.round_number / (self.session.config['numSubperiods'] +1)) % 1 != 0.0))


    def after_all_players_arrive(self):
        pass

    def vars_for_template(self):

        subperiod_timer = self.player.subperiod_time
        

        players = []
        if (self.round_number == 1): #initial price randomized in models subsession
            my_prev_price = self.player.price 
            for op in self.group.get_players():
                players.append(
                    {
                        'id':op.id_in_group,
                        'loc':op.loc, 
                        'price':op.price, 
                        'cum_payoff':sum([p.round_payoff for p in op.in_all_rounds() if ((p.round_payoff != None) & (p.period_number == self.player.period_number))])
                    }
                )
            cumulative_round_payoff = 0
        elif (self.player.period_number != self.player.in_round(self.round_number-1).period_number):
            #needs an elif here, since self.player.in_round(self.round_number-1).period_number is NULL when self.round_number == 1
            my_prev_price = self.player.price #else pull price from previous round. 

            for op in self.group.get_players():
                players.append(
                    {
                        'id':op.id_in_group,
                        'loc':op.loc, 
                        'price':op.price, 
                        'cum_payoff':sum([p.round_payoff for p in op.in_all_rounds() if ((p.round_payoff != None) & (p.period_number == self.player.period_number))])
                    }
                )
            cumulative_round_payoff = 0
        else: 
            my_prev_price = self.player.in_round(self.round_number).price #else pull price from previous round. 

            for op in self.group.get_players():
                op.price = op.in_round(self.round_number-1).next_subperiod_price
                players.append(
                    {
                        'id':op.id_in_group,
                        'loc':op.in_round(self.round_number-1).loc, 
                        'price':op.in_round(self.round_number-1).next_subperiod_price, 
                        'cum_payoff':sum([p.round_payoff for p in op.in_all_rounds() if ((p.round_payoff != None) & (p.period_number == self.player.period_number))])
                    }
                )
            cumulative_round_payoff = sum([p.round_payoff for p in self.player.in_previous_rounds() if ((p.round_payoff != None) & (p.period_number == self.player.period_number))])




        # create table of other player's loc and prices
        # use this table on the page to draw the full market place. 
        prev_market_table = []
        if self.round_number == 1: #initial price randomized in models subsession
            for plyr in self.group.get_players():
                player_data = {
                    'player_num':plyr.in_round(self.round_number).id_in_group,
                    'loc':plyr.loc,
                    'price':plyr.price,
                    'cumulative_round_payoff':0,
                }
                prev_market_table.append(player_data)
                        # this player's data.             
            other_prev_price = self.player.get_others_in_group()[0].in_round(self.round_number).price
         
        else:
            for plyr in self.group.get_players():
                player_data = {
                    'player_num':plyr.id_in_group,
                    'loc':plyr.in_round(self.round_number-1).loc,
                    'price':plyr.in_round(self.round_number-1).price,
                    'cumulative_round_payoff':sum([p.round_payoff for p in plyr.in_all_rounds() if (p.round_payoff != None)]),
                }
                prev_market_table.append(player_data)

            # this player's data.             
            my_prev_price = self.player.price #else pull price from previous round. 
            

        return {
            'players':players,
            'id_in_group':self.player.id_in_group,
            'subperiod_timer':subperiod_timer,
            'transport_cost':self.player.transport_cost,
            'round':self.player.subperiod_number,
            'num_rounds':Constants.num_rounds,
            'my_loc':self.player.loc,
            'my_prev_price':my_prev_price,
            'my_prev_price_100':my_prev_price*100,
            'cumulative_round_payoff':round(cumulative_round_payoff * 100, 3),
            'prev_market_table':prev_market_table,
            'debug':settings.DEBUG,
            'period_num':self.player.period_number,
        }

    def before_next_page(self):
        self.player.cumulative_round_payoff = sum([p.round_payoff for p in self.player.in_previous_rounds() if ((p.round_payoff != None) & (p.period_number == self.player.period_number))])

        if self.player.subperiod_number == 0:
            self.player.round_payoff = 0


class WaitPage(WaitPage):

    def after_all_players_arrive(self):
        #calc payoffs and stuff
        # self.group.set_payoffs()
        pass 


class ResultsWaitPage(WaitPage):

    def is_displayed(self):

        # if we don't have a log yet, (that is, we're in period one), then start a new log. 
        # save info from this round needed to calc final payoffs.       
        if self.round_number == (Constants.num_rounds):
            if 'exp_log' in self.participant.vars: #just error handling
              exp_log  = self.participant.vars['exp_log']
            else:
              exp_log = []

            cumulative_round_payoff = sum([(p.round_payoff / Constants.num_rounds) for p in self.player.in_all_rounds() if (p.round_payoff != None)])
            rounds = sum([1 for p in self.player.in_all_rounds() if (p.round_payoff != None)])
            
            row = {
                'period_num':(len(exp_log) + 1),
                'period_score':round(cumulative_round_payoff * 100,6),
                'paid_period':True,
                'rounds':rounds,
            }

            if (len(exp_log) + 1) == self.player.period_number:
                exp_log.append(row)
                self.participant.vars['exp_log'] = exp_log

        return self.round_number == (Constants.num_rounds)



class period_summary_review(Page):
    timeout_seconds = 10000

    form_model = models.Player
    form_fields = [
        'round_payoff','boundary_lo','boundary_hi'
        ]

    def is_displayed(self):
        return ((self.round_number / (self.session.config['numSubperiods'] +1)) % 1 == 0.0)

    def vars_for_template(self):


        players = []
        period_scores = []
        for op in self.group.get_players():
            op.price = op.in_round(self.round_number-1).next_subperiod_price
            players.append(
                {
                    'id':op.id_in_group,
                    'loc':op.in_round(self.round_number-1).loc, 
                    'price':op.in_round(self.round_number-1).next_subperiod_price, 
                    'cum_payoff':sum([p.round_payoff for p in op.in_all_rounds() if ((p.round_payoff != None) & (p.period_number == self.player.period_number))])
                }
            )

        for i in range((self.player.period_number)):
            period_scores.append(
                    {
                        'period':i+1,
                        'score':sum([p.round_payoff * 100 for p in self.player.in_previous_rounds() if ((p.round_payoff != None) & (p.period_number == (i+1)))])
                    }
                )



        cumulative_round_payoff = sum([p.round_payoff for p in self.player.in_previous_rounds() if ((p.round_payoff != None) & (p.period_number == self.player.period_number))])

        # calc all period's final scores. 

        return{
            'debug':settings.DEBUG,
            'cumulative_round_payoff':round(cumulative_round_payoff * 100, 3),
            'players':players,
            'period_scores':period_scores
        }

    def before_next_page(self):
        self.player.cumulative_round_payoff = sum([p.round_payoff for p in self.player.in_all_rounds() if ((p.round_payoff != None) & (p.period_number == self.player.period_number))])





page_sequence = [period_init_wait, WaitPage1, 
    task, WaitPage, 
    ResultsWaitPage, period_summary_review
    ]









