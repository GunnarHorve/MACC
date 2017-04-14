# ------------------------------------------------------------------------------------------------
# Copyright (c) 2016 Microsoft Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ------------------------------------------------------------------------------------------------

# Tutorial sample #2: Run simple mission using raw XML

import MalmoPython
import os
import sys
import time
import json
from AgentWrapper import AgentWrapper
import math

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately

# More interesting generator string: "3;7,44*49,73,35:1,159:4,95:13,35:13,159:11,95:10,159:14,159:6,35:6,95:6;12;"

# <ServerQuitFromTimeUp timeLimitMs="30000"/>

missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

              <About>
                <Summary>Hello world!</Summary>
              </About>

              <ServerSection>
                <ServerHandlers>
                  <FlatWorldGenerator generatorString="3;7,220*1,5*3,2;3;,biome_1"/>
                  <DrawingDecorator>
                    <DrawBlock x="5" y="227" z="5" type="stone"/>
                    <DrawBlock x="6" y="227" z="5" type="stone"/>
                    <DrawBlock x="6" y="228" z="5" type="stone"/>
                    <DrawBlock x="-5" y="227" z="-5" type="stone"/>
                    <DrawBlock x="-6" y="227" z="-5" type="stone"/>
                    <DrawBlock x="-6" y="228" z="-5" type="stone"/>
                    <DrawBlock x="5" y="227" z="-5" type="stone"/>
                    <DrawBlock x="6" y="227" z="-5" type="stone"/>
                    <DrawBlock x="6" y="228" z="-5" type="stone"/>
                    <DrawBlock x="-5" y="227" z="5" type="stone"/>
                    <DrawBlock x="-6" y="227" z="5" type="stone"/>
                    <DrawBlock x="-6" y="228" z="5" type="stone"/>
                    <DrawBlock x="0" y="228" z="0" type="gold_block"/>
                  </DrawingDecorator>
                  <ServerQuitWhenAnyAgentFinishes/>
                </ServerHandlers>
              </ServerSection>

              <AgentSection mode="Survival">
                <Name>MalmoTutorialBot</Name>
                <AgentStart/>
                <AgentHandlers>
                  <ObservationFromFullStats/>
                  <ContinuousMovementCommands turnSpeedDegs="180"/>
                </AgentHandlers>
              </AgentSection>
            </Mission>'''

# Create default Malmo objects:

agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse( sys.argv )
except RuntimeError as e:
    print 'ERROR:',e
    print agent_host.getUsage()
    exit(1)
if agent_host.receivedArgument("help"):
    print agent_host.getUsage()
    exit(0)

my_mission = MalmoPython.MissionSpec(missionXML, True)
my_mission_record = MalmoPython.MissionRecordSpec()

# Attempt to start a mission:
max_retries = 3
for retry in range(max_retries):
    try:
        agent_host.startMission( my_mission, my_mission_record )
        break
    except RuntimeError as e:
        if retry == max_retries - 1:
            print "Error starting mission:",e
            exit(1)
        else:
            time.sleep(2)

# Loop until mission starts:
print "Waiting for the mission to start ",
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    sys.stdout.write(".")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print "Error:",error.text

print
print "Mission running ",

# Boilerplate code above this point

agent = AgentWrapper(agent_host, 1)
# agent.setPosAccl(0,0,0)
Tx = 0; Ty = 228; Tz = 0 #target's x, y, and z positions
dt = 0.1                        # 1/number of updates/second
while True:
    time.sleep(0.05)
    agent.updateWorldPosition()
    agent.physicsUpdate(0.05)

    # negative because ???
    pan_des  = -math.atan2(Tx - agent.x[0], Tz - agent.z[0]) * 180. / math.pi
    tilt_des  = -math.atan2(Ty - agent.y[0], math.sqrt((Tx - agent.x[0])*(Tx - agent.x[0])+(Tz - agent.z[0])*(Tz - agent.z[0]))) * 180. / math.pi

    # scale to -180..180
    pan_cur = agent.pan[0]
    if(pan_cur > 180):
        pan_cur = pan_cur - 360
    elif(pan_cur < -180):
        pan_cur = pan_cur + 360

    # print("Cur, Desired: {}, {}".format(pan_cur, pan_des))
    reverse = 1
    if(abs(pan_cur - pan_des) > 180):
        reverse = -1

    if(pan_cur - pan_des < -2):
        agent.pan[1] = 0.1 * reverse
    elif(pan_cur - pan_des > 2):
        agent.pan[1] = -0.1 * reverse
    else:
        agent.pan[1] = 0.0

    tilt_cur = agent.tilt[0]

    if(tilt_cur - tilt_des < -2):
        agent.tilt[1] = 0.1
    elif(tilt_cur - tilt_des > 2):
        agent.tilt[1] = -0.1
    else:
        agent.tilt[1] = 0.0


    #print "agent.pan", agent.pan[1]
    #print "pan_des", pan_des

    #hi

    # print "{}, {}".format(pan_des, agent.pan[0]) #debug angle errors
    # agent.printWorldDerivatives(0)         #debug position printing
