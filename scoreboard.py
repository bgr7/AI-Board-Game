#Bugra Baygul 20190705005-072
import os
import json

class Scoreboard:
    def __init__(self, scoreboard_file="scoreboard.json"):

        self.scoreboard_file = scoreboard_file
        self.scoreboard = self.lscoreboard()

    def lscoreboard(self):

        if os.path.exists(self.scoreboard_file):
            try:
                with open(self.scoreboard_file, "r") as f:
                    data = json.load(f)

                    for mode in ['easy', 'normal', 'hard']:
                        if mode not in data:
                            data[mode] = []
                    return data
            except json.JSONDecodeError:
                print("error on scoreboard file")
        return {'easy': [], 'normal': [], 'hard': []}

    def scoreboard_saver(self):

        try:
            with open(self.scoreboard_file, "w") as f: #to save the current scoreboard to a JSON file.
                json.dump(self.scoreboard, f, indent=4)
        except Exception as e:
            print("error scoreboard save ", e) #d11

    def add_record(self, mode, name, piece_count):

        if mode not in self.scoreboard:
            self.scoreboard[mode] = []
        self.scoreboard[mode].append((name, piece_count)) # record to the scoreboard for the specified mode
        #it sorts descending by piece_count since higher is better
        self.scoreboard[mode].sort(key=lambda x: x[1], reverse=True)
        #I recorded only top 5
        self.scoreboard[mode] = self.scoreboard[mode][:5]
        self.scoreboard_saver()
