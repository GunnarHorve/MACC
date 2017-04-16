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

def drawRing(edge,type,elevation):
    for r in range(-edge, edge+1):
        my_mission.drawBlock(r, elevation, -edge, type)
        my_mission.drawBlock(r, elevation, edge, type)
        my_mission.drawBlock(edge, elevation, r, type)
        my_mission.drawBlock(-edge, elevation, r, type)

height = 227
for i in range(5,30):
    if(i%2 == 1):
        drawRing(i, "stone_slab", height)
    else:
        drawRing(i, "stone", height)
        height = height + 1

# for x in range(-30,30):
#     for y in range(227, 257):
#         my_mission.drawBlock(x, y, -30, "stone")
#         my_mission.drawBlock(x, y, 30, "stone")
#         my_mission.drawBlock(-30, y, x, "stone")
#         my_mission.drawBlock(30, y, x, "stone")

# my_mission.drawBlock(-29, 227, 29, "stone_stairs")
    # for z in range(-10,10):
    #     my_mission.drawBlock( x,227.5,z,"stone_slab")
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

flag_1 = 0;
flag_2 = 1;

while True:
    time.sleep(dt)
    agent.updateWorldPosition()
    agent.physicsUpdate(dt)
    P_Control(agent, .03)
    agent_host.sendCommand("strafe 1")

    flag_1 = flag_1 + 1

    if flag_1 > 40:
        flag_2 = flag_2*(-1)
        flag_1 = 0

    if flag_2 > 0:
        agent_host.sendCommand("move 1")
    else:
        agent_host.sendCommand("move -1")


    # agent.printWorldDerivatives(0)         #debug position printing
