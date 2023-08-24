from backtest.day_info import DayInfo

class Reporter:
    def __init__(self, report_from):
        self.report_from = report_from
        self.daily_datapoints = []

    def add(self, day_info):
        self.daily_datapoints.append(self.daily_datapoints)