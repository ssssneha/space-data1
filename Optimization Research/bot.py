import math
import json


class Bot:
    def __init__(self, x, y, z, b_range):
        self.start = [x,y,z]
        self.pos = [x, y, z]
        self.b_range = b_range
        self.cleaned = 0
        self.dist_travelled = 0
        self.path = []

    def create_similar(self):
        return Bot(self.start[0], self.start[1], self.start[2], self.b_range)

    def get_dist_sat(self, sat):
        d = math.sqrt((self.pos[0]-sat.pos[0])**2 + (self.pos[1]-sat.pos[1])**2 + (self.pos[2]-sat.pos[2])**2)
        return d
    
    def clean_debris(self, sat):
        self.cleaned += 1
        self.dist_travelled += self.get_dist_sat(sat)
        self.pos = sat.pos
        self.path.append(sat)
    
    def clean_ALL_debris(self, sats):
        #print(len(sats))
        self.path = []
        for sat in sats:
            self.clean_debris(sat)
            #print(sat)
            #print(self.dist_travelled)

    def print_path(self):
        for id,sat in enumerate(self.path):
            print(f"{id+1} {sat}")

    def print_path_json(self, output_file):
        with open(output_file, 'w') as f:
            f.write(self.pathToJSON())
        
    def __str__(self):
        return f"BOT {self.pos} {self.b_range} Cleaned {self.cleaned} dist: {self.dist_travelled}"
    
    def pathToJSON(self):
        json_string  = "[\n"
        for sat in self.path:
            json_string += sat.toJSON()
            json_string += ","
        json_string += "\n]\n"
        return json_string