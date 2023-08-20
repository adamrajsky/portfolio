from backtest.day_info import DayInfo
import json

class Logger:
    def __init__(self, output_file):
        self.output_file = output_file
        self.day_infos = []

    def log(self, day_info):
        if self.output_file == "":
            return
        self.day_infos.append(day_info.to_json_serializable_dict())

    def push(self):
        if self.output_file == "":
            return
        f = open(self.output_file, "w")
        jsonstr = json.dumps(self.day_infos, indent=4, default=str)
        f.write(jsonstr)
        f.close()


