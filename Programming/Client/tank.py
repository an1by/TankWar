import tcpip
import json

class Tank(object):    
    def __init__(self, team, number, position, dead):
        self.team = team
        self.number = number
        self.position = position
        self.dead = dead
    
    def kill(self):
        self.dead = True
    
    def move(self, position):
        command = {"command": "move", "number": self.number, "position": position}
        tcpip.send_data(command)
    
    def fire(self, target_position):
        command = {"command": "move", "number": self.number, "position": target_position}
        tcpip.send_data(command)
        result = tcpip.get_data()