# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for Launch Site
    dcc.Dropdown(id='site-dropdown',
                 options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                         [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                 value='ALL',
                 placeholder='Select a Launch Site Here',
                 searchable=True),
    html.Br(),

    # Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # Payload slider
    dcc.RangeSlider(id='payload-slider',
                    min=min_payload, max=max_payload, step=1000,
                    value=[min_payload, max_payload],
                    marks={int(min_payload): str(int(min_payload)),
                           int(max_payload): str(int(max_payload))}),
    
    # Scatter plot
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Callback for Pie Chart
@app.callback(Output('success-pie-chart', 'figure'),
              Input('site-dropdown', 'value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        success_counts = spacex_df[spacex_df['Class'] == 1]['Launch Site'].value_counts().reset_index()
        success_counts.columns = ['Launch Site', 'Successes']
        fig = px.pie(success_counts, values='Successes', names='Launch Site',
                     title='Total Success Launches by Site')
    else:
        site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        class_counts = site_df['Class'].value_counts().reset_index()
        class_counts.columns = ['Class', 'Count']
        fig = px.pie(class_counts, values='Count', names='Class',
                     title=f'Success vs. Failure for site {entered_site}')
    return fig

# Callback for Scatter Plot
@app.callback(Output('success-payload-scatter-chart', 'figure'),
              [Input('site-dropdown', 'value'),
               Input('payload-slider', 'value')])
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                            (spacex_df['Payload Mass (kg)'] <= high)]
    
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='Class',
                         color='Booster Version',
                         title='Correlation between Payload and Success for All Sites')
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='Class',
                         color='Booster Version',
                         title=f'Correlation between Payload and Success for {entered_site}')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)