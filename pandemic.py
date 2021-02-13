import dash
import dash_html_components as html
import plotly.express as px
import dash_core_components as dcc
import time
from random import random
from math import sqrt

t = time.time()

Dist = 10 #danger distance
D1 = 1 #after 2 days he ll be infected
D2 = 10 #after 5 days he ll recover
T = 100 #simulation time
N = 1000 #population size
Rx = 100#range of x axis
Ry = 100#range of y axis

df = []
# columns = ["time", "agent_num","counter","status","x","y"]

# Time frame
df.append([])
Time = 0
for i in range(0,T):
    df[Time] = df[Time] + ([i]*N)

# Agent numb
df.append([])
Agent = 1
for i in range(0,T):
    df[Agent] = df[Agent] + list(range(0,N))

#try smt to see if it gonna speed up

# Initialisation agents at T = 0
Susceptible = 0
Infectious = 1
Recovered = 2
#### Initialise counters
df.append([0]*N)
Counter = 2

#### Initialise states
df.append(([Susceptible]*(N-2)) + [Infectious] + [Recovered])
State = 3

#### Initialise Position
df.append([(int( random() * ((2*Rx)+1) )-Rx) for i in range(N)])
X = 4
df.append([(int( random() * ((2*Ry)+1) )-Ry) for i in range(N)])
Y = 5


# Proceed with the evolution in time
for i in range(1, T):
    # find the infected agents in t = i-1
    I = []
    for j in range(0,N):
        if(df[State][((i-1)*N)+j]==Infectious):
            I.append(((i-1)*N)+j)
    for j in range(0, N):

        # update state and counter according to previous states and position
        if(df[State][((i-1)*N)+j]==Infectious):
            if(df[Counter][((i-1)*N)+j] == D2):
                df[State].append(Recovered)
                df[Counter].append(0)
            else:
                df[State].append(Infectious)
                df[Counter].append(df[Counter][((i-1)*N)+j] + 1)
        elif (df[State][((i - 1) * N) + j] == Susceptible):
            StillAppend = True
            for k in I:
                D = sqrt(pow((df[X][k]-df[X][((i - 1) * N) + j]),2) + pow((df[Y][k]-df[Y][((i - 1) * N) + j]),2))
                if (D <= Dist):
                    if(df[Counter][((i-1)*N)+j] == D1):
                        df[State].append(Infectious)
                        df[Counter].append(0)
                    else:
                        df[State].append(Susceptible)
                        df[Counter].append(df[Counter][((i-1)*N)+j] +1)
                    StillAppend = False
                    break #i have to test this
            if(StillAppend):
                df[State].append(Susceptible)
                df[Counter].append(0)
        else:
            df[State].append(Recovered)
            df[Counter].append(0)

        # new position
        df[X].append(df[X][((i-1)*N)+j] + (int( random() * 3 )-1))
        df[Y].append(df[Y][((i - 1) * N) + j] + (int( random() * 3 )-1))


fig = px.scatter(x=df[X], y=df[Y], animation_frame = df[Time], animation_group=df[Agent], hover_name=df[Agent], color=df[State], width=1000, height=700)

#print(df)
print("%.100f" % (time.time()-t))

app = dash.Dash()
# then you should let me live a little and go to study but no pain no gain right
app.layout = html.Div([
    html.Div(html.H1("It is working")),
    html.Div(
        dcc.Graph(figure = fig)
    ),
    htm l.Div(),
])

if __name__=="__main__" :
    app.run_server(debug = True)