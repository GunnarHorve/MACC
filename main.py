import MalmoPython
import os
import sys
import time
import json
from AgentWrapper import AgentWrapper
import math

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately

# load the world
mission_file = './drawMe.xml'
with open(mission_file, 'r') as f:
    print "Loading mission from %s" % mission_file
    mission_xml = f.read()
    my_mission = MalmoPython.MissionSpec(mission_xml, True)
# add 20% holes for interest
# for x in range(1,4):
#     for z in range(1,13):
#         if random.random()<0.1:
#             my_mission.drawBlock( x,45,z,"lava")
# Create default Malmo objects:

# connect to server
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

################## Boilerplate code above this point ##########################

# performs a basic propotional control loop to set both angular velocities
def P_Control(agent, P):
    # negative because ???
    pan_des  = -math.atan2(Tx - agent.x[0], Tz - agent.z[0]) * 180. / math.pi

    pan_cur = agent.pan[0]  #scale to -180..180
    if(pan_cur > 180):
        pan_cur = pan_cur - 360
    elif(pan_cur < -180):
        pan_cur = pan_cur + 360

    reverse = 1             # determine if left spin or right spin is closer
    if(abs(pan_cur - pan_des) > 180):
        reverse = -1
    agent.pan[1] = P * (pan_des - pan_cur) * reverse

    tilt_des  = -math.atan2(Ty - agent.y[0], math.sqrt((Tx - agent.x[0])*(Tx - agent.x[0])+(Tz - agent.z[0])*(Tz - agent.z[0]))) * 180. / math.pi
    tilt_cur = agent.tilt[0]
    agent.tilt[1] = P * (tilt_des - tilt_cur)

agent = AgentWrapper(agent_host, 1)
Tx = 0; Ty = 227; Tz = 0 #target's x, y, and z positions
dt = 0.05                        # 1/number of updates/second

while True:
    time.sleep(dt)
    agent.updateWorldPosition()
    agent.physicsUpdate(dt)
    P_Control(agent, .01)

    # agent.printWorldDerivatives(0)         #debug position printing
