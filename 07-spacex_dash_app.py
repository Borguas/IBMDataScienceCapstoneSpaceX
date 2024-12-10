# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                                            [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                                    value='ALL',
                                    placeholder="Select a Launch Site",
                                    style={'width': '50%', 'padding': '3px', 'font-size': '20px', 'margin': '10px auto'}
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                html.Div(dcc.RangeSlider(
                                        id='payload-slider',
                                        min=0,  # Convertimos min_payload a entero
                                        max=10000,  # Convertimos max_payload a entero
                                        step=1000,
                                        value=[min_payload, max_payload],  # También convertimos el valor inicial a entero
                                    ),
                                    style={'width': '80%', 'margin': '0 auto'}  # Aplica el estilo al contenedor del slider
                                ),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Group by success status and create a pie chart
        success_counts = spacex_df[spacex_df['class'] == 1]
        success_site_counts = success_counts.groupby('Launch Site').size().reset_index(name='count')
        fig = px.pie(success_site_counts, names='Launch Site', values='count', 
                     title="Total Success Launches by Site")
    else:
        # Filter the data based on the selected site and group by success status
        site_data = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_counts = site_data.groupby('class').size().reset_index(name='count')
        fig = px.pie(success_counts, names='class', values='count', 
                     title=f"Success vs Failed Launches at {selected_site}")

    return fig


# TASK 4: Callback function to update scatter chart based on selected site and payload range
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range

    # Filter the data based on payload range
    filtered_data = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                              (spacex_df['Payload Mass (kg)'] <= high)]
    
    if selected_site != 'ALL':
        # Filter by site if one is selected
        filtered_data = filtered_data[filtered_data['Launch Site'] == selected_site]

    # Create a scatter plot for success vs payload
    fig = px.scatter(filtered_data, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category', title="Payload Mass vs Launch Success",
                     labels={'class': 'Success (1) / Failure (0)'})
    
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
