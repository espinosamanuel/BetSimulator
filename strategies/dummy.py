from abc import ABC
import strategies.base_strategy as bs
import core.utils as core_utils
import strategies.utils as strats_utils


class Strategy(bs.BaseStrategy, ABC):
    perimeter = ['I1']

    def accept(self, row):
        if not self.in_perimeter(row):
            return False

        return True

    def aggregate(self, events):
        events.sort_values(by=['BetOdd'], inplace=True)

        sel_events = []
        for index, row in events.head(2).iterrows():
            event = strats_utils.Event(row)
            sel_events.append(event)

        return [strats_utils.Bet(sel_events)]

    def select_out(self, row):
        odds = {}
        for column in core_utils.odds_columns:
            odds[column] = row[column]

        return min(odds, key=odds.get)

    def get_bet_amount(self):
        return 2
