import cPickle as pickle
import plotly.plotly as py
import plotly.graph_objs as go

tilts = pickle.load(open("Test_Data/tilts.p", "rb")) # [[desired], [actual]]
pans = pickle.load(open("Test_Data/pans.p", "rb"))   # [[desired], [actual]]
times = pickle.load(open("Test_Data/times.p", "rb")) # seconds

pan_diffs = []
tilt_diffs = []
for i in range(len(tilts[0])):
    tilt_diffs.append(tilts[1][i] - tilts[0][i])
    pan_diffs.append(pans[1][i] - pans[0][i])

# Create traces
trace0 = go.Scatter(
    x = times,
    y = pan_diffs,
    mode = 'lines',
    name = 'pan error'
)
trace1 = go.Scatter(
    x = times,
    y = tilt_diffs,
    mode = 'lines',
    name = 'tilt error'
)

py.sign_in('GunnarHorve', '5li4IKu0I69Iv2ETBVgC')
py.iplot([trace0], filename='Pan Errors')
py.iplot([trace1], filename='Tilt Errors')