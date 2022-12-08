from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

app = Dash(__name__)

df = pd.read_csv("crimedata.csv", delimiter=',')

# All crimes by states
# -------------------------------------------------------------------
df_crime_per_state = df[["state", "arsons", "autoTheft", "larcenies",
                         "burglaries", "assaults", "robberies", "rapes", "murders"]]

crime_types = list(df_crime_per_state)
crime_types.remove('state')
df_crime_per_state["All crimes"] = df_crime_per_state[crime_types].sum(axis=1)
df_crime_per_state = df_crime_per_state.groupby(["state"]).sum().reset_index()

fig = go.Figure(data=go.Choropleth(
    locations=df_crime_per_state['state'],
    z=df_crime_per_state['All crimes'].astype(int),
    locationmode='USA-states',
    colorscale='Reds',
    colorbar_title="Crimes",
))

fig.update_layout(
    # autosize=False,
    # width=700,
    # height= 1200,
    title_text='2018 Crime amount',
    geo_scope='usa',
)
# -------------------------------------------------------------------

fig_1 = go.Figure()
crime_types.append('All crimes')

# -------------------------------------------------------------------
type_by_comm = df[["communityName", "state", "arsons", "autoTheft", "larcenies",
                   "burglaries", "assaults", "robberies", "rapes", "murders"]]

fig_2 = px.bar()
fig_2.update_layout(title="Click on the state to see more information")

# -------------------------------------------------------------------
fig_3 = px.bar()
fig_3.update_layout(title="Select State")
# --------------------------------------------------------------------

fig_4 = px.bar()
fig_4.update_layout(title="Click on the bar to see more information anout community")
# --------------------------------------------------------------------
app.layout = html.Div(children=[
    html.H1(children='Analysis of crime and population in the USA', style={'textAlign': 'center', 'color': '#A52A2A'}),
    html.Div(children='''
        Data taken from:
        https://www.kaggle.com/datasets/michaelbryantds/crimedata
    '''),

    html.H2(children='Crime statistics', style={'textAlign': 'center', 'color': '#A52A2A'}),

    html.Div([
        dcc.Markdown('Select crime type:'),
        dcc.Dropdown(crime_types, 'All crimes', id='crime_dropdown'),
    ]),

    dcc.Graph(
        id='US_map',
        figure=fig,
        clickData={'points': [{'location': None}]}
    ),
    html.Div([
        html.Div([
            dcc.Markdown('Ratio of types of crime'),
            dcc.Graph(
                id='Crime_types',
                figure=fig_1,
            ),
        ]),
        html.Div([
            dcc.Graph(
                id='Community_type',
                figure=fig_4,
            ),
        ]),
    ], style={'columnCount': 2, 'align': 'center'}),

    html.H2(children='Population', style={'textAlign': 'center', 'color': '#A52A2A'}),

    html.Div([
        dcc.Markdown('Select state:'),
        dcc.Dropdown(df.state.unique(), 'OR', id='state_dropdown'),
    ]),
    html.Div([
        html.Div([
            dcc.Graph(
                id='Bar_states',
                figure=fig_3,
                clickData={'points': [{'label': None}]}
            ),
        ]),
        html.Div([
            dcc.Graph(
                id='Community_pop',
                figure=fig_4,
            ),
        ]),
    ], style={'columnCount': 2, 'align': 'center'}),

    html.Div([
        dcc.Markdown('Please rate the work: '),
        dcc.Slider(0, 10, 1, value=5)
    ]),

    html.H2(children='Thanks for watching', style={'textAlign': 'center', 'color': '#A52A2A'}),
    html.H4(children='Created by Almas, december 2022', style={'textAlign': 'right', 'color': '#000000'})
])


@callback(
    Output('US_map', 'figure'),
    Input('crime_dropdown', 'value')
)
def update_map(crime):
    if crime is None:
        fig = go.Figure()
        fig.update_layout(title="Click on the state to see more information")
        return fig
    fig = go.Figure(data=go.Choropleth(
        locations=df_crime_per_state['state'],
        z=df_crime_per_state[crime].astype(int),
        locationmode='USA-states',
        colorscale='Reds',
    ))
    fig.update_layout(
        title_text="Number of " + crime,
        geo_scope='usa',
    )
    return fig


@callback(
    Output('Crime_types', 'figure'),
    Input('US_map', 'clickData')
)
def display_click_state_crime_types(clickData):
    state = clickData["points"][0]["location"]
    cr_types = ["arsons", "autoTheft", "larcenies",
                "burglaries", "assaults", "robberies", "rapes", "murders"]
    if state is None:
        crime_types_qty = df_crime_per_state[cr_types].sum(axis=0).reset_index()
        crime_types_qty = pd.DataFrame(data={"Type": crime_types_qty.iloc[:, 0],
                                             "qty": crime_types_qty.iloc[:, 1]})
        fig_1 = px.pie(crime_types_qty, values=crime_types_qty.qty,
                       names=crime_types_qty.Type, title="Crime types")
        return fig_1

    state_crime_type = df[["state", "arsons", "autoTheft", "larcenies",
                           "burglaries", "assaults", "robberies", "rapes", "murders"]][df["state"] == state]
    state_crime_type = state_crime_type[cr_types].sum(axis=0).reset_index()
    state_crime_type = pd.DataFrame(data={"Type": state_crime_type.iloc[:, 0],
                                          "qty": state_crime_type.iloc[:, 1]})
    fig_1 = px.pie(state_crime_type, values=state_crime_type.qty,
                   names=state_crime_type.Type, title="Crimes by types in " + state + " state")

    return fig_1


@callback(
    Output('Community_type', 'figure'),
    Input('US_map', 'clickData')
)
def display_click_data_walk(clickData):
    state = clickData["points"][0]["location"]
    if state is None:
        fig_2 = go.Figure()
        fig_2.update_layout(title="Click on the state to see more information")
        return fig_2
    cr_types = ["arsons", "autoTheft", "larcenies",
                "burglaries", "assaults", "robberies", "rapes", "murders"]

    type_by_comm = df[["communityName", "state", "arsons", "autoTheft", "larcenies",
                       "burglaries", "assaults", "robberies", "rapes", "murders"]][df["state"] == state]
    type_by_comm = type_by_comm.melt(id_vars=["communityName"], value_vars=cr_types)

    type_by_comm = type_by_comm.groupby(["variable", "communityName"]).agg({"value": "sum"}).reset_index() \
        .rename(columns={"variable": "crime_type", "value": "crimes_qty"})

    fig_2 = (px.bar(type_by_comm, y="crime_type",
                    x='crimes_qty',
                    color="communityName"))
    return fig_2


@callback(
    Output('Bar_states', 'figure'),
    Input('state_dropdown', 'value')
)
def update_bar_states(state):
    population_df = df[["state", "communityName", "population", "racePctWhite", "racepctblack", "racePctAsian",
                        "racePctHisp", "agePct12t21", "agePct12t29", "agePct16t24", "agePct65up"]][df.state == state]

    population_by_com = population_df.groupby(["communityName"]).agg({"population": "sum"}).reset_index()
    fig_3 = px.bar(population_by_com, x="population", y="communityName")
    fig_3.update_layout(
        title_text=state + ' population',
    )
    return fig_3


@callback(
    Output('Community_pop', 'figure'),
    Input('Bar_states', 'clickData')
)
def update_community_pop(clickData):
    community = clickData["points"][0]["label"]
    if community is None:
        fig_4 = go.Figure()
        fig_4.update_layout(title="Click on the community to see more information")
        return fig_4
    population_by_comm = \
        df[["communityName", "racePctWhite", "racepctblack", "racePctAsian", "PctEmploy", "PctUnemployed",
            "racePctHisp"]][
            df.communityName == community]
    ethnic = ["racePctWhite", "racepctblack", "racePctAsian", "racePctHisp"]
    population_by_comm_ethnic = population_by_comm.melt(id_vars=["communityName"], value_vars=ethnic) \
        .rename(columns={"variable": "ethnic", "value": "percentage"})
    print(population_by_comm_ethnic)

    fig_4 = make_subplots(rows=2, cols=1, specs=[[{"type": "bar"}], [{"type": "pie"}]])
    fig_4.add_trace(go.Bar(
        x=["Employed", "Unemployed"],
        y=[population_by_comm.iloc[0]["PctEmploy"], population_by_comm.iloc[0]["PctUnemployed"]],
        marker_color=["aqua", "tomato"]
    ), row=1, col=1)

    labels = population_by_comm_ethnic.ethnic.tolist()
    values = population_by_comm_ethnic.percentage.tolist()
    fig_4.add_trace(go.Pie(labels=labels, values=values),
                    row=2, col=1)

    fig_4.update_layout(
        title_text="Unemployment level and race statistics in " + community
    )
    return fig_4


if __name__ == '__main__':
    app.run_server(debug=True)
