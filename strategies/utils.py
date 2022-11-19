

class Event:
    def __init__(self, row):
        self.week = row.VirtualWeek
        self.match = row.HomeTeam + ' - ' + row.AwayTeam
        self.result = row.FTR
        self.bet_result = row.Bet
        self.win = row.Win
        self.odd = row[self.bet_result]


class Bet:

    def __init__(self, events):
        self.events = events
