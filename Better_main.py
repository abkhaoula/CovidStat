import csv
from datetime import timedelta
from datetime import datetime
import plotly.graph_objs as go
import dash
import dash_html_components as html
import dash_core_components as dcc

# read data
data = []
with open("assets/patients-maroc.csv", "r") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    for line in csv_reader:
        i = len(line)
        break
    j = 0
    while(j<i):
        data.append([])
        j = j +1
    for line in csv_reader:
        i = 0
        for elem in line:
            data[i].append(elem)
            i = i+1

# drop the variables with too much missing values :
data.pop(1)  # "sex"
data.pop(1)  # "age"
data.pop(1)  # "country"
data.pop(2)  # "disease"
data.pop(2)  # "group"
data.pop(2)  # "infection_order"
data.pop(2)  # "exposure_start"
data.pop(3)  # "exposure_end"
data.pop(3)  # "infected_by"
data.pop(3)  # "contact_number"

######
#header = ['\ufeffn', 'province', 'infection_reason', 'confirmed_date', 'released_date', 'deceased_date', 'state']
######
# to a better coding experience
n = 0
province = 1
infection_reason = 2
confirmed_date = 3
released_date = 4
deceased_date = 5
state = 6

# 2 dead with no deceased_date (drop them)
l = len(data[0])
a = 0
for i in range(0, l):
    if ((data[state][i - a] == "Deceased") & (data[deceased_date][i - a] == "")):
        for j in range(0,state+1):
            data[j].pop(i - a)
        a = a + 1

# 1 exits with death date: (replave exit with Deceased)
l = len(data[0])
for i in range(0, l):
    if ((data[state][i] == "Exit") & (data[deceased_date][i] != "")):
        data[state][i] = "Deceased"

# 1 exits with no released_date (delete it)
a = 0
for i in range(0, l):
    if ((data[state][i - a] == "Exit") & (data[released_date][i - a] == "")):
        for j in range(0, state+1):
            data[j].pop(i - a)
        a = a + 1

# replace the missing values of infection_reason with an Unknown reason
l = len(data[0])
for i in range(0, l):
    if (data[infection_reason][i] == ""):
        data[infection_reason][i] = "Unknown"

# standerise the reason format
for i in range(0, l):
    if (data[infection_reason][i] == "local"):
        data[infection_reason][i] = "Local"
    elif (data[infection_reason][i] == "imported"):
        data[infection_reason][i] = "Imported"

# generate an infection reason table
infection_reasons = [[], []]
for i in range(0,l):
    if (data[infection_reason][i] != ""):
        found = False
        lC = len(infection_reasons[0])
        for j in range(0,lC):
            if (data[infection_reason][i] == infection_reasons[0][j]):
                infection_reasons[1][j] = infection_reasons[1][j] + 1
                found = True
        if (not found):
            infection_reasons[0].append(data[infection_reason][i])
            infection_reasons[1].append(1)


# convert the dates variables from string to datetime
for i in range(0,l):
    if(data[confirmed_date][i] != ""):
        if(len(data[confirmed_date][i])>8):
            data[confirmed_date][i] = datetime.strptime(data[confirmed_date][i][:-2], "%m/%d/%y")
        else:
            data[confirmed_date][i] = datetime.strptime(data[confirmed_date][i], "%m/%d/%y")
    if (data[released_date][i] != ""):
        data[released_date][i] = datetime.strptime(data[released_date][i], "%m/%d/%y")
    if (data[deceased_date][i] != ""):
        data[deceased_date][i] = datetime.strptime(data[deceased_date][i], "%m/%d/%y")

# if nothing is declared in a given day note it as 0
cases_daily = [[],[]]
for i in range(0,l):
    if (data[confirmed_date][i] != ""):
        found = False
        lC = len(cases_daily[0])
        for j in range(0,lC):
            if (data[confirmed_date][i] == cases_daily[0][j]):
                cases_daily[1][j] = cases_daily[1][j] + 1
                found = True
        if (not found):
            cases_daily[0].append(data[confirmed_date][i])
            cases_daily[1].append(1)

deaths_daily = [[],[]]
for i in range(0,l):
    if (data[deceased_date][i] != ""):
        found = False
        lC = len(deaths_daily[0])
        for j in range(0,lC):
            if (data[deceased_date][i] == deaths_daily[0][j]):
                deaths_daily[1][j] = deaths_daily[1][j] + 1
                found = True
        if (not found):
            deaths_daily[0].append(data[deceased_date][i])
            deaths_daily[1].append(1)

releases_daily = [[],[]]
for i in range(0,l):
    if (data[released_date][i] != ""):
        found = False
        lC = len(releases_daily[0])
        for j in range(0,lC):
            if (data[released_date][i] == releases_daily[0][j]):
                releases_daily[1][j] = releases_daily[1][j] + 1
                found = True
        if (not found):
            releases_daily[0].append(data[released_date][i])
            releases_daily[1].append(1)

#find min and max
lC = len(cases_daily[0])
min = cases_daily[0][0]
max = min
for i in range(0,lC):
    if (cases_daily[0][i] < min):
        min = cases_daily[0][i]
    elif (cases_daily[0][i] > max):
        max = cases_daily[0][i]

#generate the days
day_num = max-min
days = []
d = timedelta(days = 0)
while(d <= day_num):
    days.append(cases_daily[0][0] + d)
    d = d + timedelta(days = 1)

#if the day is not in the data add it with o record
for i in days:
    found = False
    for case in cases_daily[0]:
        if (case == i):
            found = True
    if (not found):
        cases_daily[0].append(i)
        cases_daily[1].append(0)

    found = False
    for case in deaths_daily[0]:
        if (case == i):
            found = True
    if (not found):
        deaths_daily[0].append(i)
        deaths_daily[1].append(0)

    found = False
    for case in releases_daily[0]:
        if (case == i):
            found = True
    if (not found):
        releases_daily[0].append(i)
        releases_daily[1].append(0)

#sort everything
lC = len(cases_daily[0])
for i in range(0,lC-1):
    for j in range(i+1,lC):
        if (cases_daily[0][i] > cases_daily[0][j]):
            for k in range(0,2):
                temp = cases_daily[k][j]
                cases_daily[k][j] = cases_daily[k][i]
                cases_daily[k][i] = temp

lC = len(deaths_daily[0])
for i in range(0,lC-1):
    for j in range(i+1,lC):
        if (deaths_daily[0][i] > deaths_daily[0][j]):
            for k in range(0,2):
                temp = deaths_daily[k][j]
                deaths_daily[k][j] = deaths_daily[k][i]
                deaths_daily[k][i] = temp

lC = len(releases_daily[0])
for i in range(0,lC-1):
    for j in range(i+1,lC):
        if (releases_daily[0][i] > releases_daily[0][j]):
            for k in range(0,2):
                temp = releases_daily[k][j]
                releases_daily[k][j] = releases_daily[k][i]
                releases_daily[k][i] = temp

#accumulate
accumulate_cases = cases_daily
accumulate_deaths = deaths_daily
accumulate_releases = releases_daily
for i in range(1, lC):
    accumulate_cases[1][i] = accumulate_cases[1][i-1] + cases_daily[1][i]
    accumulate_deaths[1][i] = accumulate_deaths[1][i - 1] + deaths_daily[1][i]
    accumulate_releases[1][i] = accumulate_releases[1][i - 1] + releases_daily[1][i]

# generate daily traces
trace_cases_daily = go.Scatter(x = list(cases_daily[0]),
                               y = list(cases_daily[1]),
                               name = "cases_daily",
                               mode= "lines",
                               line = dict(color = "#0852a1"))
trace_deaths_daily = go.Scatter(x = list(deaths_daily[0]),
                               y = list(deaths_daily[1]),
                               name = "death_daily",
                               mode= "lines",
                               line = dict(color = "#d40b0b"))
trace_releases_daily = go.Scatter(x = list(releases_daily[0]),
                               y = list(releases_daily[1]),
                               name = "releases_daily",
                               mode= "lines",
                               line = dict(color = "#1aa108"))

# generate accumulate traces
trace_accumulate_cases = go.Scatter(x = list(accumulate_cases[0]),
                                    y = list(accumulate_cases[1]),
                                    name = "accumulate_cases",
                                    mode= "lines",
                                    line = dict(color = "#0852a1"))
trace_accumulate_deaths = go.Scatter(x = list(accumulate_deaths[0]),
                                    y = list(accumulate_deaths[1]),
                                    name = "accumulate_deaths",
                                    mode= "lines",
                                    line = dict(color = "#d40b0b"))
trace_accumulate_releases = go.Scatter(x = list(accumulate_releases[0]),
                                    y = list(accumulate_releases[1]),
                                    name = "accumulate_releases",
                                    mode= "lines",
                                    line = dict(color = "#1aa108"))

#donut chart
trace_infection_reasons = go.Pie(labels = infection_reasons[0],
                                 values = infection_reasons[1],
                                 hole=.5)

# construct a data of recordes per province

province_cases = []
lon = [-7.965636,-8.365910,-4.658982,-6.235980,-5.433289,-6.267116,-8.634435,-2.556609,-9.875821,-5.330057,-13.178729]
lat = [33.134399,31.736601,33.726610,34.140537,35.197405,32.492824,29.992446,33.991792,28.581917,31.258876,27.131740]
province_cases.append(lon)
province_cases.append(lat)
province_cases.append([])
province_cases.append([])
province_cases.append([])
province_cases.append([])

# to a better coding experience
lon = 0
lat = 1
name = 2
isolated = 3
dead = 4
exited = 5

for i in range(0,l):
    if (data[province][i] != ""):
        found = False
        lC = len(province_cases[2])
        for j in range(0,lC):
            if (data[province][i] == province_cases[2][j]):
                found = True
                if (data[state][i] == "isolated"):
                    province_cases[isolated][j] = province_cases[isolated][j] + 1
                elif (data[state][i] == "Deceased"):
                    province_cases[dead][j] = province_cases[dead][j] + 1
                elif (data[state][i] == "Exit"):
                    province_cases[exited][j] = province_cases[exited][j] + 1
        if (not found):
            province_cases[2].append(data[province][i])
            province_cases[isolated].append(0)
            province_cases[dead].append(0)
            province_cases[exited].append(0)
            if(data[state][i] == "isolated"):
                province_cases[isolated][-1] = 1
            elif (data[state][i] == "Deceased"):
                province_cases[dead][-1] = 1
            elif (data[state][i] == "Exit"):
                province_cases[exited][-1] = 1
#Index(['Casablanca - Settat', 'Marrakech - Safi', 'Rabat - Sale - Kenitra','Fes - Meknes', 'Tanger - Tetouan - Al Houceima', 'Oriental','Daraa - Tafilalet', 'Beni Mellal - Khenifra', 'Souss - Massa','Laayoune - Saguia al hamra', 'Guelmim - Oued Noun'],dtype='object')
#      ['Casablanca - Settat', 'Marrakech - Safi', 'Fes - Meknes', 'Rabat - Sale - Kenitra', 'Tanger - Tetouan - Al Houceima', 'Beni Mellal - Khenifra', 'Souss - Massa', 'Oriental', 'Guelmim - Oued Noun', 'Daraa - Tafilalet', 'Laayoune - Saguia al hamra']


#traces for a geo plot
trace_isolated_geo = go.Scattergeo(
    name = "isolated",
    locationmode = 'country names',
    lon = province_cases[lon],
    lat = province_cases[lat],
    text = province_cases[name],
    marker = dict(
        sizeref=.1,
        size = province_cases[isolated],
        sizemode = "area",
    ),
    hovertemplate=
        "<b>%{text}</b><br>" +
        "Number of: %{marker.size}<br>" +
        "<extra></extra>",
)
trace_deceased_geo = go.Scattergeo(
    name = "deceased",
    locationmode = 'country names',
    lon=province_cases[lon],
    lat=province_cases[lat],
    text=province_cases[name],
    marker = dict(
        sizeref=.1,
        size = province_cases[dead],
        sizemode = "area",
    ),
    hovertemplate=
        "<b>%{text}</b><br>" +
        "Number of: %{marker.size}<br>" +
        "<extra></extra>",
)
trace_exit_geo = go.Scattergeo(
    name = "exit",
    locationmode = 'country names',
    lon=province_cases[lon],
    lat=province_cases[lat],
    text=province_cases[name],
    marker = dict(
        sizeref=.1,
        size = province_cases[exited],
        sizemode = "area"
    ),
    hovertemplate=
        "<b>%{text}</b><br>" +
        "Number of: %{marker.size}<br>" +
        "<extra></extra>",
)


#traces for a bar chart
trace_isolated = go.Bar(
    x = province_cases[name],
    y = province_cases[isolated],
    name = "isolated"
)
trace_deceased = go.Bar(
    x = province_cases[name],
    y = province_cases[dead],
    name = "deceased"
)
trace_exit = go.Bar(
    x = province_cases[name],
    y = province_cases[exited],
    name = "exit"
)

#create the app to display
app = dash.Dash()

# append the css
app.css.config.serve_locally = False
app.css.append_css({
    'external_url':"https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"
})

# construct the layout
app.layout = html.Div([
    html.Div(html.H1("Hello World")),
    html.Label("Dash app"),
    html.Div([
        html.Div([
            html.H3(["Cases Dayly"]),
            dcc.Graph(
                figure ={"data":[trace_cases_daily,trace_deaths_daily,trace_releases_daily],
                         "layout":{"title":"Number of recorded covid-19 cases dayly"}
                         },
            ),
        ], className="col-6"),
        html.Div([
            html.H3(["Accumulate Cases"]),
            dcc.Graph(
                figure ={"data":[trace_accumulate_cases,trace_accumulate_deaths,trace_accumulate_releases],
                         "layout":{"title":"Number of recorded covid-19 until each day"}
                         },
            ),
        ], className="col-6"),
    ], className="row"),
    html.Div([
        dcc.Graph(
            figure={
                "data": [trace_infection_reasons],
                "layout":{"title":"Infection reasons",
                          "scope": 'africa'},

            }
        )
    ]),
    html.H3(id = "date_selected"),
    html.Div([
        dcc.Slider(
            id="date_selector",
            min=0,
            max=(day_num).days,
            step = 1,
            value=(day_num).days,
        )
    ]),
    html.Div([
        html.Div([
            dcc.Graph(
                id = "geo_fig",
                figure={
                    "data": [trace_isolated_geo,trace_deceased_geo,trace_exit_geo],
                    "layout":{"title":"Map view",
                              "legend": {'itemsizing': 'constant'},
                              "geo":{"resolution":50,
                                     "showframe": False,
                                     "showland" : True,"framewidth": 1000,
                                     "landcolor" : "rgb(217, 217, 217)",
                                     "fitbounds": "locations",
                                     "showcoastlines":True, "coastlinecolor":"White",
                                     "showcountries": True,"countrycolor": "White"},
                              "hoverinfo": "text",
                              }
                }
            )
        ], className="col-5"),
        html.Div([
            dcc.Graph(
                id = "bar_chart",
                figure ={
                    "data": [trace_isolated,trace_deceased,trace_exit],
                    "layout": {"title": "Bar Chart"}
                }
            )
        ], className="col-7"),
    ], className="row"),
])

#callback to update the day displayed
@app.callback(
    dash.dependencies.Output("date_selected", "children"),
    [dash.dependencies.Input("date_selector", "value")])
def update_date_text(value):
    return '{}'.format(days[value].strftime("%d %b %Y"))

#callback to update the bar chart
@app.callback(
    dash.dependencies.Output("bar_chart", "figure"),
    [dash.dependencies.Input("date_selector", "value")])
def update_bar_chart(value):
    province_cases.pop(-1)
    province_cases.pop(-1)
    province_cases.pop(-1)
    lC = len(province_cases[2])
    province_cases.append([0]*lC)
    province_cases.append([0]*lC)
    province_cases.append([0]*lC)
    for i in range(0, l):
        for j in range(0, lC):
            if (data[province][i] == province_cases[2][j]):
                if (data[state][i] == "isolated"):
                    if(data[confirmed_date][i] <= days[value]):
                        province_cases[isolated][j] = province_cases[isolated][j] + 1
                elif (data[state][i] == "Deceased"):
                    if (data[deceased_date][i] <= days[value]):
                        province_cases[dead][j] = province_cases[dead][j] + 1
                elif (data[state][i] == "Exit"):
                    if (data[released_date][i] <= days[value]):
                        province_cases[exited][j] = province_cases[exited][j] + 1

    # traces for a bar chart
    trace_isolated = go.Bar(
        x=province_cases[name],
        y=province_cases[isolated],
        name="isolated"
    )
    trace_deceased = go.Bar(
        x=province_cases[name],
        y=province_cases[dead],
        name="deceased"
    )
    trace_exit = go.Bar(
        x=province_cases[name],
        y=province_cases[exited],
        name="exit"
    )
    return {"data": [trace_isolated,trace_deceased,trace_exit],
            "layout": {"title": "Bar Chart"}}

#update the geo fig
@app.callback(
    dash.dependencies.Output("geo_fig", "figure"),
    [dash.dependencies.Input("date_selector", "value")])
def update_geo_fig(value):
    # traces for a geo plot
    trace_isolated_geo = go.Scattergeo(
        name="isolated",
        locationmode='country names',
        lon=province_cases[lon],
        lat=province_cases[lat],
        text=province_cases[name],
        marker=dict(
            sizeref=.1,
            size=province_cases[isolated],
            sizemode="area",
        ),
        hovertemplate=
        "<b>%{text}</b><br>" +
        "Number of: %{marker.size}<br>" +
        "<extra></extra>",
    )
    trace_deceased_geo = go.Scattergeo(
        name="deceased",
        locationmode='country names',
        lon=province_cases[lon],
        lat=province_cases[lat],
        text=province_cases[name],
        marker=dict(
            sizeref=.1,
            size=province_cases[dead],
            sizemode="area",
        ),
        hovertemplate=
        "<b>%{text}</b><br>" +
        "Number of: %{marker.size}<br>" +
        "<extra></extra>",
    )
    trace_exit_geo = go.Scattergeo(
        name="exit",
        locationmode='country names',
        lon=province_cases[lon],
        lat=province_cases[lat],
        text=province_cases[name],
        marker=dict(
            sizeref=.1,
            size=province_cases[exited],
            sizemode="area"
        ),
        hovertemplate=
        "<b>%{text}</b><br>" +
        "Number of: %{marker.size}<br>" +
        "<extra></extra>",
    )
    return {"data": [trace_isolated_geo,trace_deceased_geo,trace_exit_geo],
            "layout":{"title":"Map view",
                      "legend": {'itemsizing': 'constant'},
                      "geo":{"resolution":50,
                             "showframe": False,
                             "showland" : True,"framewidth": 1000,
                             "landcolor" : "rgb(217, 217, 217)",
                             "fitbounds": "locations",
                             "showcoastlines":True, "coastlinecolor":"White",
                             "showcountries": True,"countrycolor": "White"},
                      "hoverinfo": "text",}
            }


if __name__=="__main__" :
    app.run_server(debug = True)
