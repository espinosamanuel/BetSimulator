import importlib
import os
import core.utils
import core.utils as utils
import pandas as pd
import matplotlib.pyplot as plt
import logging as log
from matplotlib.backends.backend_pdf import PdfPages

log.basicConfig(level=log.INFO, format='%(name)s - %(levelname)s - %(message)s')


class Simulation:
    """This class is a representation of the simulation flow.

    :param strategy: The name of the used strategy
    :type strategy: str
    :param bets: The list of :class:`core.backtester.Bet` used in the simulation
    :type bets: list
    :param balance_df: A dataframe containing the weekly time series of the balance
    :type balance_df: `pandas.DataFrame`
    :param wins: The number of won bets
    :type wins: int
    :param defeats: The number of lost bets
    :type defeats: int
    :param seasons: The list of seasons used in the simulation
    :type seasons: list

    """
    def __init__(self, strategy):
        self.strategy = strategy
        self.bets = []
        self.balance_df = pd.DataFrame()
        self.balance_df['week'] = 0
        self.balance_df['balance'] = 0
        self.balance_df['cash'] = 0
        self.wins = 0
        self.defeats = 0
        self.seasons = []


def test(strategy_name):
    """This function back-tests the strategy given as input. The test result is generated in the output directory."""

    log.info('Backtester starting...')
    log.info('Strategy: '+strategy_name)

    if strategy_name is None:
        raise Exception('Strategy parameter is required')

    sim = Simulation(strategy_name)

    log.info('Validating strategy...')
    strategy_class = getattr(importlib.import_module('strategies.' + strategy_name), 'Strategy')
    strategy = strategy_class()
    log.info('Strategy is valid')

    balance = cash = 0
    for season_file in sorted(os.listdir(utils.data_path)):
        season = season_file.replace('.csv', '').split('_')[1]
        log.info('Start season: '+season)

        sf = pd.read_csv(os.path.join(utils.data_path, season_file))

        weeks = sf.VirtualWeek.unique()

        week_first = None
        for week in weeks:
            log.debug('Week: '+str(week))
            events = []
            fsf = sf[sf.VirtualWeek == week].dropna()
            for index, row in fsf.iterrows():
                if strategy.accept(row):
                    row['Bet'] = strategy.get_bet(row)
                    row['BetOdd'] = row[row.Bet]
                    row['Win'] = row.Bet == row.FTR
                    events.append(row)

            log.debug('Accepted Events: '+str(len(events)))
            if len(events) > 0:
                log.debug('Aggregating...')
                sim.bets = strategy.aggregate(pd.DataFrame(events))
                log.debug('Aggregation has been completed. Bets: '+str(len(sim.bets)))
                log.debug('Start betting...')
                for bet in sim.bets:
                    bet.odd = 1
                    bet.is_win = True
                    for event in bet.events:
                        bet.week = event.week
                        bet.odd = bet.odd * event.odd
                        bet.is_win = bet.is_win and event.win
                        if week_first is None:
                            week_first = str(season) + '_' + str(event.week)
                            sim.seasons.append(season)

                    bet.amount = strategy.get_bet_amount()
                    cash += bet.amount
                    if bet.is_win:
                        bet.win = bet.amount * bet.odd
                        balance += bet.win
                        sim.wins += 1
                    else:
                        bet.win = 0
                        balance += - bet.amount
                        sim.defeats += 1

                    strategy.context['simulation'] = sim

                log.debug('End betting.')
            sim.balance_df.loc[len(sim.balance_df.index)] = [str(season) + '_' + str(week), balance, cash]
            log.debug('End week: '+str(week))
        log.info('End season: '+str(season))

    core.utils.replace_directory(core.utils.output_path)

    with PdfPages(os.path.join(core.utils.output_path, sim.strategy+'_out.pdf')) as pdf:
        # Line Chart
        plt.figure()
        plt.plot(sim.balance_df.week, sim.balance_df.cash, label='Cash', color='#5271ff')
        plt.plot(sim.balance_df.week, sim.balance_df.balance, label='Bet', color='#ea4335')
        plt.xlabel('Seasons')
        plt.ylabel('Balance')
        plt.legend(["Cash", "Strategy"])
        ax = plt.gca()
        ax.set_xticks(ax.get_xticks()[::(len(sim.balance_df.index)//5)])
        labels = []
        for label in (item.get_text() for item in ax.get_xticklabels()):
            labels.append(label.split("_")[0])

        ax.set_xticklabels(labels)
        plt.title("Strategy:"+sim.strategy)
        pdf.savefig()
        plt.close()

        # Pie Chart
        colors = ['#3aa757', '#ea4335']
        plt.figure()
        labels = 'Wins', 'Defeats'
        sizes = [sim.wins, sim.defeats]
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax1.axis('equal')
        ax1.set_title("Strategy:"+sim.strategy)
        pdf.savefig()
        plt.close()

    log.info('Backtester end')

