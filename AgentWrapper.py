import MalmoPython
import os
import sys
import time
import json

class AgentWrapper:
    agent_host = 0
    m = 0
    b_pos = 0
    b_ang = 0

    pan = [0.0, 0.0, 0.0]
    tilt = [0.0, 0.0, 0.0]

    x = [-9.5, 0.0, 0.0]
    y = [227.0, 0.0, 0.0]
    z = [-9.5, 0.0, 0.0]

    def __init__(self, agent_host, m, b_pos, b_ang):
        self.agent_host = agent_host
        self.m = m
        self.b_pos = b_pos
        self.b_ang = b_ang

    def setAngAccl(self, yaw_a, pitch_a): #pan, tilt
        self.pan[2] = yaw_a
        self.tit[2] = pitch_a

    def setPosAccl(self, x_a, y_a, Z_a):
        self.x[2] = x_a
        self.y[2] = y_a
        self.z[2] = z_a

    def updateWorldPosition(self):
        # get most recent observations
        world_state = self.agent_host.getWorldState()
        for error in world_state.errors:
            print "Error:",error.text
        obs = json.loads( world_state.observations[-1].text )

        # save observations to class
        self.x[0] = obs[u'XPos']
        self.y[0] = obs[u'YPos']
        self.z[0] = obs[u'ZPos']
        self.pan[0] = obs[u'Yaw']
        self.tilt[0] = obs[u'Pitch']

    def printWorldPos(self):
        s = '|  x,y,z: ({:.2f}, {:.2f}, {:.2f})  |  pan,tilt: ({:.2f}, {:.2f})  |'
        print s.format(self.x[0],self.y[0],self.z[0],self.pan[0],self.tilt[0])
