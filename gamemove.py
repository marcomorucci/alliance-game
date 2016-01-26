class GameMove(object):
    def __init__(self, unit=None, origin=None, destination=None, action=None, target=None):
        self.origin = origin
        self.destination = destination
        self.action = action
        self.target = target
        self.unit = unit

    def __eq__(self, other):
        return self.origin.id == other.origin.id and \
            self.destination.id == other.destination.id and \
            self.action == other.action and self.target.id == other.target.id
        
    def __str__(self):
        return "origin: node " + str(self.origin.id) + "\n" + \
            "destination: node " + str(self.destination.id) + "\n" + \
            "action: " + self.action + "\n" + "target: node " + str(self.target.id)