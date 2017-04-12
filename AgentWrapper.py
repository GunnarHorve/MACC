import MalmoPython
import os
import sys
import time
import json

class AgentWrapper:
    agent_host = 0
    b = 0

    pan = [0.0, 0.0, 0.0]
    tilt = [0.0, 0.0, 0.0]

    x = [-9.5, 0.0, 0.0]
    y = [227.0, 0.0, 0.0]
    z = [-9.5, 0.0, 0.0]

    def __init__(self, agent_host, b):
        self.agent_host = agent_host
        self.b = b

    def setAngAccl(self, yaw_a, pitch_a): #pan, tilt
        self.pan[2] = yaw_a
        self.tit[2] = pitch_a

    def setPosAccl(self, x_a, y_a, z_a):
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

    def printWorldDerivatives(self, d):
        s = '{}st derivatives |  x,y,z: ({:.2f}, {:.2f}, {:.2f})  |  pan,tilt: ({:.2f}, {:.2f})  |'
        print s.format(d, self.x[d],self.y[d],self.z[d],self.pan[d],self.tilt[d])

    def physicsUpdate(self, dt):
        # temporary variable storage
        x = self.x; y = self.y; z = self.z
        pan = self.pan; tilt = self.tilt

        # position updates are handled by simulation

        # update velocities in wrapper
        self.x[1] = self.updateVel(x, dt)
        self.y[1] = self.updateVel(y, dt)
        self.z[1] = self.updateVel(z, dt)
        self.pan[1] = self.updateVel(pan, dt)
        self.tilt[1] = self.updateVel(tilt, dt)

        # acceleration updates are handled by controller

        # updating velocities in simulation
        self.sendCommandHelper('move ', self.x[1])
        # self.agent_host.sendCommandHelper('jump ', self.y[1])
        self.sendCommandHelper('strafe ', self.z[1])
        self.sendCommandHelper('turn ', self.pan[1])
        self.sendCommandHelper('pitch ', self.tilt[1])

    def updateVel(self, dim, dt):
        ans = dim[1] + (dim[2] - self.b*dim[1])*dt  # vanilla
        print self.b
        if(dim[2] == 0 and abs(ans) > abs(dim[1])): #see if friction stopped us
            ans = 0
        elif(ans > 1):                              # see if we're too fast
            ans = 1
        elif(ans < -1):                             # see if we're too slow
            ans = -1
        return ans

    def sendCommandHelper(self, command, magnitude):
        if(magnitude > 1):
            magnitude = 1
        if(magnitude < -1):
            magnitude = -1
        self.agent_host.sendCommand(command + str(magnitude))
