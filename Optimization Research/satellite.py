import json

class Satellite:    
    def init(self, id, type, x, y, z):
        self.id = id
        self.type = type
        self.pos = [x, y, z]

    def import_line(self, arr):
        self.init(arr[0], arr[1], float(arr[2]), float(arr[3]), float(arr[4]))

    def __str__(self):
        return f"{self.id} {self.type} {self.pos}"
    
    def __repr__(self) -> str:
        return f"{self.id} {self.type} {self.pos}"
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    