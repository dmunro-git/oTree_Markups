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
        return self.player.subperiod_number == 0




class task(Page):   
    # timeout_seconds = 10
    # timeout_submission = {'price': 1}

    form_model = models.Player
    form_fields = [
        'next_subperiod_price','prev_round_payoff','boundary_lo','boundary_hi'
        ]
  
  
    def is_displayed(self):
        return (
            (self.player.subperiod_number <= (self.session.config['numSubperiods']))
            & (self.player.period_number <= len(self.session.config['t']))
        ) # summary info round


    def after_all_players_arrive(self):
        pass

    def vars_for_template(self):

        subperiod_timer = self.player.subperiod_time
        

        players = []
        if (self.player.subperiod_number == 0): #initial price randomized in models subsession
            my_prev_price = self.player.price
            transport_cost = self.player.transport_cost
            mc = self.player.mc
            rp = self.player.rp

            for op in self.group.get_players():
                players.append(
                    {
                        'subperiod_num': self.player.subperiod_number,
                        'period_num':self.player.period_number,
                        'id':op.id_in_group,
                        'loc':op.loc, 
                        'price':op.price, 
                        'cum_payoff':sum([p.prev_prev_round_payoff for p in op.in_all_rounds() if ((p.prev_round_payoff != None) & (p.period_number == self.player.period_number))])
                    }
                )
            prev_round_cumulative_payoff = 0.0
        else: 

            p_lastRound = self.player.in_round(self.round_number-1)
            my_prev_price = p_lastRound.next_subperiod_price #else pull price from previous round. 
            transport_cost = p_lastRound.transport_cost
            mc = p_lastRound.mc,
            rp = p_lastRound.rp,

            for op in self.group.get_players():

                op.price = op.in_round(self.round_number-1).next_subperiod_price

                players.append(
                    {
                        'subperiod_num': self.player.subperiod_number,
                        'period_num':self.player.period_number,
                        'id':op.id_in_group,
                        'loc':op.in_round(self.round_number-1).loc, 
                        'price':op.in_round(self.round_number-1).next_subperiod_price, 
                        'cum_payoff':sum([p.prev_round_payoff for p in op.in_all_rounds() if ((p.prev_round_payoff != None) & (p.period_number == self.player.period_number))])
                    }
                )

            prev_round_cumulative_payoff = sum([p.prev_round_payoff for p in self.player.in_previous_rounds() if ((p.prev_round_payoff != None) & (p.period_number == self.player.period_number))])



        return {
            'players':players,
            'id_in_group':self.player.id_in_group,
            'subperiod_timer':subperiod_timer,
            'transport_cost':transport_cost,
            'mc':mc,
            'rp':rp,
            'round':self.player.subperiod_number,
            'num_rounds':Constants.num_rounds,
            'my_loc':self.player.loc,
            'my_prev_price':my_prev_price,
            'my_prev_price_100': my_prev_price * 100,
            'prev_round_cumulative_payoff':round(prev_round_cumulative_payoff * 100, 3),
            'debug':settings.DEBUG,
            'period_num':self.player.period_number,
        }

    def before_next_page(self):
            self.player.prev_round_cumulative_payoff = sum([p.prev_round_payoff for p in self.player.in_previous_rounds() if ((p.prev_round_payoff != None) & (p.period_number == self.player.period_number))])


class WaitPage(WaitPage):

    def after_all_players_arrive(self):
        #calc payoffs and stuff
        # self.group.set_payoffs()
        pass 





class period_summary_review(Page):
    timeout_seconds = 30

    form_model = models.Player
    form_fields = [
        'prev_round_payoff','boundary_lo','boundary_hi'
        ]

    def is_displayed(self):
            return( 
                (self.player.subperiod_number == (self.session.config['numSubperiods'] + 1))
                & (self.player.period_number <= len(self.session.config['t']))
            )
            

    def vars_for_template(self):




        # needed to set scores for final subpeirod
        my_prev_price = self.player.in_round(self.round_number-1).next_subperiod_price #else pull price from previous round. 
        transport_cost = self.player.in_round(self.round_number-1).transport_cost
        mc = self.player.in_round(self.round_number-1).mc,
        rp = self.player.in_round(self.round_number-1).rp,
        players = []
        for op in self.group.get_players():

            op.price = op.in_round(self.round_number-1).next_subperiod_price

            players.append(
                {
                    'subperiod_num': self.player.subperiod_number,
                    'period_num':self.player.period_number,
                    'id':op.id_in_group,
                    'loc':op.in_round(self.round_number-1).loc, 
                    'price':op.in_round(self.round_number-1).next_subperiod_price, 
                    'cum_payoff':sum([p.prev_round_payoff for p in op.in_all_rounds() if ((p.prev_round_payoff != None) & (p.period_number == self.player.period_number))])
                }
            )

        prev_round_cumulative_payoff = sum([p.prev_round_payoff for p in self.player.in_previous_rounds() if ((p.prev_round_payoff != None) & (p.period_number == self.player.period_number))])


        # get period scores
        period_scores = []
        for period in range(1,self.player.period_number+1):
            period_scores.append(
                {
                    'period':period,
                    'score':sum([p.prev_round_payoff for p in self.player.in_previous_rounds() if ((p.prev_round_payoff != None) & (p.period_number == period))]) * 100

                }
            )
        

        # get subperiod scores fro debug
        numSubperiods = self.session.config['numSubperiods']
        last_periods_scores = []
        for subperd in range(0,numSubperiods+1):

            if (self.player.in_round(self.round_number-(numSubperiods-subperd)).prev_round_payoff != None):
                score = self.player.in_round(self.round_number-(numSubperiods-subperd)).prev_round_payoff * 100
            else: 
                score = None

            if (self.player.in_round(self.round_number-(numSubperiods-subperd-1)).prev_round_cumulative_payoff != None):
                cum_score = self.player.in_round(self.round_number-(numSubperiods-subperd-1)).prev_round_cumulative_payoff * 100
            else:
                cum_score = None


            last_periods_scores.append(
                {
                'subperiod':subperd,
                'period_number':self.player.in_round(self.round_number-(numSubperiods-subperd+1)).period_number,
                't':self.player.in_round(self.round_number-(numSubperiods-subperd+1)).transport_cost,
                'mc':self.player.in_round(self.round_number-(numSubperiods-subperd+1)).mc,
                'rp':self.player.in_round(self.round_number-(numSubperiods-subperd+1)).rp,
                'loc':self.player.in_round(self.round_number-(numSubperiods-subperd+1)).loc,
                'price':self.player.in_round(self.round_number-(numSubperiods-subperd+1)).next_subperiod_price,
                'score':score,
                'cum_score':cum_score,
                }
            )


        return{
            'period':self.player.period_number,
            'round':self.round_number,
            'debug':settings.DEBUG,
            'transport_cost':transport_cost,
            'mc':mc,
            'rp':rp,
            'prev_round_cumulative_payoff':round(prev_round_cumulative_payoff * 100, 3),
            'players':players,
            'period_scores':period_scores,
            'last_periods_scores':last_periods_scores,
            'my_prev_price':my_prev_price,
            'id_in_group':self.player.id_in_group,
            'numberofsubperiods_less1':self.session.config['numSubperiods'] - 1,

        }

    def before_next_page(self):
        self.player.prev_round_cumulative_payoff = sum([p.prev_round_payoff for p in self.player.in_previous_rounds() if ((p.prev_round_payoff != None) & (p.period_number == self.player.period_number))])

        # get period scores
        period_scores = []
        for period in range(1,self.player.period_number+1):
            period_scores.append(
                {
                    'period':period,
                    'score':sum([p.prev_round_payoff for p in self.player.in_previous_rounds() if ((p.prev_round_payoff != None) & (p.period_number == period))]) * 100

                }
            )
            
        self.participant.vars['period_scores'] = period_scores




page_sequence = [
    period_init_wait, WaitPage1, 
    task, 
    WaitPage, 
    period_summary_review
    ]









