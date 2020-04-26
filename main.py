import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
#from dash.dependencies import Input, Output

#data intro
df = pd.read_csv("assets/patients-maroc.csv")

# too much missing values : print(df.isnull().sum())
df.drop(["sex","age","country","disease","group","infection_order","exposure_start","exposure_end","infected_by","contact_number"],axis = 1,inplace = True)
# 2 dead with no deceased_date : print(df[df["state"]=="Deceased"][["state","released_date","deceased_date"]])
df = df.drop(df[(df["state"]=="Deceased") & (df["deceased_date"].isnull())].index)
# 1 exits with no released_date and 1 exits with death date: print(df[df["state"]=="Exit"][["state","released_date","deceased_date"]])
df = df.drop(df[(df["state"]=="Exit") & (df["released_date"].isnull()) & (df["deceased_date"].isnull())].index)
df.loc[40] = df.loc[40].replace(to_replace = ["Exit"],value = "Deceased")


# replace the missing values of infection_reason with an Unknown reason and standerise the reason format
df.infection_reason.fillna("Unknown", inplace = True)
df.replace(to_replace = ["local"], value = "Local", inplace = True)
df.replace(to_replace = ["imported"], value = "Imported", inplace = True)
infection_reasons = df.infection_reason.value_counts()



#converting to the right type : print(df.dtypes)
df["confirmed_date"] =pd.to_datetime(df.confirmed_date)
df["released_date"] =pd.to_datetime(df.released_date)
df["deceased_date"] =pd.to_datetime(df.deceased_date)



# if nothing is declared in a given day note it as 0
cases_daily = df.confirmed_date.value_counts()
cases_daily = cases_daily.sort_index()
deaths_daily = df.deceased_date.value_counts()
releases_daily = df.released_date.value_counts()
day_num = (cases_daily.index)[-1]-(cases_daily.index)[0]
days = pd.date_range((cases_daily.index)[0], (cases_daily.index)[-1], freq="D")
days.append(pd.date_range((cases_daily.index)[0], periods=1,freq="D"))
for i in days:
    if i not in cases_daily.index:
        cases_daily = cases_daily.append(pd.Series([0], index=[i]))
    if i not in deaths_daily.index:
        deaths_daily = deaths_daily.append(pd.Series([0], index=[i]))
    if i not in releases_daily.index:
        releases_daily = releases_daily.append(pd.Series([0], index=[i]))
#sort everything
cases_daily = cases_daily.sort_index()
deaths_daily = deaths_daily.sort_index()
releases_daily = releases_daily.sort_index()



#accumulate valuesfor i in cases_daily.index:
sum_cases = 0
accumulate_cases = cases_daily.copy()
sum_deaths = 0
accumulate_deaths = deaths_daily.copy()
sum_releases = 0
accumulate_releases = releases_daily.copy()
for i in days:
    sum_cases = sum_cases + cases_daily[i]
    accumulate_cases[i] = sum_cases
    sum_deaths = sum_deaths + deaths_daily[i]
    accumulate_deaths[i] = sum_deaths
    sum_releases = sum_releases + releases_daily[i]
    accumulate_releases[i] = sum_releases




# generate daily traces
trace_cases_daily = go.Scatter(x = list(cases_daily.index),
                               y = list(cases_daily.values),
                               name = "cases_daily",
                               mode= "lines",
                               line = dict(color = "#0852a1"))
trace_deaths_daily = go.Scatter(x = list(deaths_daily.index),
                               y = list(deaths_daily.values),
                               name = "death_daily",
                               mode= "lines",
                               line = dict(color = "#d40b0b"))
trace_releases_daily = go.Scatter(x = list(releases_daily.index),
                               y = list(releases_daily.values),
                               name = "releases_daily",
                               mode= "lines",
                               line = dict(color = "#1aa108"))




# generate accumulate traces
trace_accumulate_cases = go.Scatter(x = list(accumulate_cases.index),
                                    y = list(accumulate_cases.values),
                                    name = "accumulate_cases",
                                    mode= "lines",
                                    line = dict(color = "#0852a1"))
trace_accumulate_deaths = go.Scatter(x = list(accumulate_deaths.index),
                                    y = list(accumulate_deaths.values),
                                    name = "accumulate_deaths",
                                    mode= "lines",
                                    line = dict(color = "#d40b0b"))
trace_accumulate_releases = go.Scatter(x = list(accumulate_releases.index),
                                    y = list(accumulate_releases.values),
                                    name = "accumulate_releases",
                                    mode= "lines",
                                    line = dict(color = "#1aa108"))


#donut chart
trace_infection_reasons = go.Pie(labels = infection_reasons.index,
                                 values = infection_reasons.values,
                                 hole=.5)



# construct a data of recordes per province
df_sub = pd.DataFrame(df[df.state == "isolated"].province.value_counts())
df_sub.columns = ["isolated"]
lon = [-7.965636,-8.365910,-6.235980,-4.658982,-5.433289,-2.556609,-5.330057,-6.267116,-8.634435,-13.178729,-9.875821]
lat = [33.134399,31.736601,34.140537,33.726610,35.197405,33.991792,31.258876,32.492824,29.992446,27.131740,28.581917]
deceased = df[df.state == "Deceased"].province.value_counts()
exit = df[df.state == "Exit"].province.value_counts()
df_sub["lon"] = lon
df_sub["lat"] = lat
df_sub["deceased"] = deceased
df_sub["exit"] = exit
df_sub.fillna(0, inplace=True)


#traces for a geo plot
trace_isolated_geo = go.Scattergeo(
    name = "isolated",
    locationmode = 'country names',
    lon = df_sub.lon,
    lat = df_sub.lat,
    text = df_sub.index,
    marker = dict(
        sizeref=.1,
        size = df_sub.isolated,
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
    lon = df_sub.lon,
    lat = df_sub.lat,
    text = df_sub.index,
    marker = dict(
        sizeref=.1,
        size = df_sub.deceased,
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
    lon = df_sub.lon,
    lat = df_sub.lat,
    text = df_sub.index,
    marker = dict(
        sizeref=.1,
        size = df_sub.exit,
        sizemode = "area"
    ),
    hovertemplate=
        "<b>%{text}</b><br>" +
        "Number of: %{marker.size}<br>" +
        "<extra></extra>",
)

#traces for a bar chart
trace_isolated = go.Bar(
    x = df_sub.index,
    y = df_sub.isolated,
    name = "isolated"
)
trace_deceased = go.Bar(
    x = df_sub.index,
    y = df_sub.deceased,
    name = "deceased"
)
trace_exit = go.Bar(
    x = df_sub.index,
    y = df_sub.exit,
    name = "exit"
)
print((df.state == "isolated") & (df.confirmed_date <= days[5]))





#create the app to display
app = dash.Dash()
app.css.config.serve_locally = False
# append the css
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
    html.Div([
        dcc.Graph(
            id = "geo_fig",
            figure={
                "data": [trace_isolated_geo,trace_deceased_geo,trace_exit_geo],
                "layout":{"title":"Map view",
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
    ]),
    html.Div([
        dcc.Graph(
            id = "bar_chart",
            figure ={
                "data": [trace_isolated,trace_deceased,trace_exit],
                "layout": {"title": "Bar Chart"}
            }
        )
    ]),
    html.Div([
        dcc.Slider(
            id="date_selector",
            min=0,
            max=(df.confirmed_date.max()-df.confirmed_date.min()).days,
            step = 1,
            value=(df.confirmed_date.max()-df.confirmed_date.min()).days,
        )
    ]),
    html.H3(id = "date_selected"),
])

#callback to update the day displayed
@app.callback(
    dash.dependencies.Output("date_selected", "children"),
    [dash.dependencies.Input("date_selector", "value")])
def update_date_text(value):
    print(value)
    return '{}'.format(days.strftime("%d %b %Y")[value])


#callback to update the bar chart
@app.callback(
    dash.dependencies.Output("bar_chart", "figure"),
    [dash.dependencies.Input("date_selector", "value")])
def update_bar_chart(value):
    isolated = df[(df.state == "isolated") & (df.confirmed_date <= days[value])].province.value_counts()
    deceased = df[(df.state == "Deceased") & (df.confirmed_date <= days[value])].province.value_counts()
    exit = df[(df.state == "Exit") & (df.confirmed_date <= days[value])].province.value_counts()
    df_sub["isolated"] = isolated
    df_sub["deceased"] = deceased
    df_sub["exit"] = exit
    df_sub.fillna(0, inplace=True)
    print(df_sub)
    # traces for a bar chart
    trace_isolated = go.Bar(
        x=df_sub.index,
        y=df_sub.isolated,
        name="isolated"
    )
    trace_deceased = go.Bar(
        x=df_sub.index,
        y=df_sub.deceased,
        name="deceased"
    )
    trace_exit = go.Bar(
        x=df_sub.index,
        y=df_sub.exit,
        name="exit"
    )
    return {"data": [trace_isolated,trace_deceased,trace_exit],
            "layout": {"title": "Bar Chart"}}



#update the geo fig
@app.callback(
    dash.dependencies.Output("geo_fig", "figure"),
    [dash.dependencies.Input("date_selector", "value")])
def update_geo_fig(value):
    isolated = df[(df.state == "isolated") & (df.confirmed_date <= days[value])].province.value_counts()
    deceased = df[(df.state == "Deceased") & (df.confirmed_date <= days[value])].province.value_counts()
    exit = df[(df.state == "Exit") & (df.confirmed_date <= days[value])].province.value_counts()
    df_sub["isolated"] = isolated
    df_sub["deceased"] = deceased
    df_sub["exit"] = exit
    df_sub.fillna(0, inplace=True)
    print(df_sub)
    # traces for a bar chart
    trace_isolated_geo = go.Scattergeo(
        name = "isolated",
        locationmode='country names',
        lon=df_sub.lon,
        lat=df_sub.lat,
        text=df_sub.index,
        marker=dict(
            sizeref=.1,
            size=df_sub.isolated,
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
        lon=df_sub.lon,
        lat=df_sub.lat,
        text=df_sub.index,
        marker=dict(
            sizeref=.1,
            size=df_sub.deceased,
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
        lon=df_sub.lon,
        lat=df_sub.lat,
        text=df_sub.index,
        marker=dict(
            sizeref=.1,
            size=df_sub.exit,
            sizemode="area"
        ),
        hovertemplate=
        "<b>%{text}</b><br>" +
        "Number of: %{marker.size}<br>" +
        "<extra></extra>",
    )
    return {"data": [trace_isolated_geo,trace_deceased_geo,trace_exit_geo],
            "layout":{"title":"Was testing",
                      "geo":{"resolution":50,
                             "showframe": False,
                             "showland" : True,"framewidth": 1000,
                             "landcolor" : "rgb(217, 217, 217)",
                             "fitbounds": "locations",
                             "showcoastlines":True, "coastlinecolor":"White",
                             "showcountries": True,"countrycolor": "White"},
                      "hoverinfo": "text",}}




if __name__=="__main__" :
    app.run_server(debug = True)