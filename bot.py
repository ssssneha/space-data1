import math


class Bot:
    def __init__(self, x, y, z, b_range):
        self.pos = [x, y, z]
        self.b_range = b_range
        self.cleaned = 0
        self.dist_travelled = 0
        self.path = []

    def create_similar(self):
        return Bot(self.pos[0], self.pos[1], self.pos[2], self.b_range)

    def get_dist_sat(self, sat):
        d = math.sqrt((self.pos[0]-sat.pos[0])**2 + (self.pos[1]-sat.pos[1])**2 + (self.pos[2]-sat.pos[2])**2)
        return d
    
    def clean_debris(self, sat):
        self.cleaned += 1
        self.dist_travelled += self.get_dist_sat(sat)
        self.pos = sat.pos
        self.path.append(sat)
    
    def clean_ALL_debris(self, sats):
        for sat in sats:
            self.clean_debris(sat)
            print(self.dist_travelled)

    def print_path(self):
        for id,sat in enumerate(self.path):
            print(f"{id+1} {sat}")
        

        