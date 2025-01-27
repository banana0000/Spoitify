import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from pypalettes import load_cmap

cmap = load_cmap("Acadia")
colors = cmap.colors

# Load dataset
file_path = 'spotify_history.csv'
data = pd.read_csv(file_path)

# Data preprocessing
data['ts'] = pd.to_datetime(data['ts'])
data['date'] = data['ts'].dt.date

# Calculate KPIs
kpi_total_tracks = data['track_name'].count()
kpi_total_hours = round(data['ms_played'].sum() / (1000 * 60 * 60), 2)
kpi_top_artist = data['artist_name'].mode()[0]
kpi_top_track = data['track_name'].mode()[0]

# Dropdown options for artist filter
artist_options = [{'label': artist, 'value': artist} for artist in data['artist_name'].unique()]

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = 'Spotify Dashboard'
app.config.suppress_callback_exceptions = True

# Define the layout for the dashboard page
def dashboard_layout():
    return dbc.Container([ 
        dbc.Row([
            dbc.Col([  # Logo on the left
                html.Img(
                    src='https://upload.wikimedia.org/wikipedia/commons/2/26/Spotify_logo_with_text.svg',
                    style={'width': '200px', 'height': 'auto'}
                )
            ], width=3, className='mb-4'),

            dbc.Col([], width=6),  # Empty column for spacing

            dbc.Col([  # Dropdown on the right
                dbc.Select(
                    id='artist-filter',
                    options=artist_options,
                    placeholder='Select Artist',
                    value=None,
                    style={
                        'backgroundColor': '#121212',
                        'color': 'white',
                        'border': '1px solid #28a745',
                        'borderRadius': '5px',
                        'padding': '10px',
                        'fontSize': '16px',
                        'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.2)',
                        'cursor': 'pointer'
                    }
                )
            ], width=3, className='mb-4')
        ], className='align-items-center mb-4'),

        dbc.Row([  # Row for KPI Cards
            dbc.Col( 
                dbc.Card( 
                    dbc.CardBody([ 
                        html.H2('Total Tracks Played', className='card-title', style={'color': '#fff', 'fontWeight': 'bold'}), 
                        html.P(f'{kpi_total_tracks}', className='card-text', style={'fontSize': '34px', 'color': '#fff', 'fontWeight': 'bold'}) 
                    ]), 
                    style={'text-align':'center','background': 'linear-gradient(135deg, #1DB954, #191414)', 'border': 'none', 'boxShadow': '0px 4px 10px rgba(0, 0, 0, 0.5)', 'padding': '15px'} 
                ), 
                width=3, className="mb-4"
            ),
            dbc.Col( 
                dbc.Card( 
                    dbc.CardBody([ 
                        html.H3('Total Listening Hours', className='card-title', style={'color': '#fff', 'fontWeight': 'bold'}), 
                        html.P(f'{kpi_total_hours}', className='card-text', style={'fontSize': '34px', 'color': '#fff', 'fontWeight': 'bold'}) 
                    ]), 
                    style={'text-align':'center','background': 'linear-gradient(135deg,rgb(142, 175, 182),rgb(22, 75, 151))', 'border': 'none', 'boxShadow': '0px 4px 10px rgba(0, 0, 0, 0.5)', 'padding': '15px'} 
                ), 
                width=3, className="mb-4"
            ),
            dbc.Col( 
                dbc.Card( 
                    dbc.CardBody([ 
                        html.H3('Top Artist', className='card-title', style={'color': '#fff', 'fontWeight': 'bold'}), 
                        html.P(f'{kpi_top_artist}', className='card-text', style={'fontSize': '34px', 'color': '#fff', 'fontWeight': 'bold'}) 
                    ]), 
                    style={'text-align':'center','background': 'linear-gradient(135deg,rgb(122, 104, 203),rgb(52, 18, 100))', 'border': 'none', 'boxShadow': '0px 4px 10px rgba(0, 0, 0, 0.5)', 'padding': '15px'} 
                ), 
                width=3, className="mb-4"
            ),
            dbc.Col( 
                dbc.Card( 
                    dbc.CardBody([ 
                        html.H3('Top Track', className='card-title', style={'color': '#fff', 'fontWeight': 'bold'}), 
                        html.P(f'{kpi_top_track}', className='card-text', style={'fontSize': '34px', 'color': '#fff', 'fontWeight': 'bold'}) 
                    ]), 
                    style={'text-align':'center', 'background': 'linear-gradient(135deg,rgb(159, 198, 92),rgb(62, 97, 13))', 'border': 'none', 'boxShadow': '0px 4px 10px rgba(0, 0, 0, 0.5)', 'padding': '15px'} 
                ), 
                width=3, className="mb-4"
            ),
        ], className='mb-4'),

        dbc.Row([ 
            dbc.Col(dcc.Graph(id='trend-chart'), width=12, lg=6, className='mb-4'), 
            dbc.Col(dcc.Graph(id='artist-chart'), width=12, lg=6, className='mb-4') 
        ]),

        dbc.Row([ 
            dbc.Col(dcc.Graph(id='reason-donut-chart'), width=12, sm=6, lg=4, className='mb-4'), 
            dbc.Col(dcc.Graph(id='platform-donut-chart'), width=12, sm=6, lg=4, className='mb-4'), 
            dbc.Col(html.Img(id='word-cloud', style={'width': '100%', 'height': 'auto', 'maxHeight': '400px'}), width=12, sm=6, lg=4, className='mb-4') 
        ]) 
    ], fluid=True, style={'backgroundColor': '#121212', 'height': '100vh', 'padding': '20px 50px'})  # Adjust padding for whole container

# Set initial layout
app.layout = html.Div([ 
    dcc.Location(id='url', refresh=False), 
    html.Div(id='page-content') 
])

# Callback to handle page navigation
@app.callback( 
    Output('page-content', 'children'), 
    [Input('url', 'pathname')] 
)
def display_page(pathname):
    return dashboard_layout()

# Callbacks to update charts based on selected artist
@app.callback( 
    [Output('trend-chart', 'figure'), 
     Output('artist-chart', 'figure'), 
     Output('reason-donut-chart', 'figure'), 
     Output('platform-donut-chart', 'figure'), 
     Output('word-cloud', 'src')], 
    [Input('artist-filter', 'value')] 
)
def update_charts(selected_artist): 
    filtered_data = data if not selected_artist else data[data['artist_name'] == selected_artist]

    # Listening Trends Over Time
    listening_trends = filtered_data.groupby('date')['ms_played'].sum().reset_index()
    listening_trends['hours_played'] = listening_trends['ms_played'] / (1000 * 60 * 60)
    trend_chart = px.line(listening_trends, x='date', y='hours_played', template='plotly_dark', color_discrete_sequence=['#28a745'])
    trend_chart.update_layout(
        title='Listening Trends Over Time', 
        yaxis_title=None, 
        xaxis_title=None,  # Remove x-axis title
        margin={'l': 0, 'r': 0, 't': 50, 'b': 0}  # Adjust margins
    )

    # Top Artists - Reverse order by play count
    top_artists = filtered_data['artist_name'].value_counts().head(10).reset_index()
    top_artists.columns = ['artist_name', 'play_count']
    top_artists = top_artists.sort_values('play_count', ascending=True)
    artist_chart = px.bar(top_artists, x='play_count', y='artist_name', orientation='h', template='plotly_dark', color_discrete_sequence=['#28a745'])
    artist_chart.update_layout(
        title='Top Artists by Play Count', 
        yaxis_title=None, 
        xaxis_title=None, 
        margin={'l': 0, 'r': 0, 't': 50, 'b': 0}  # Adjust margins
    )

    # Playback Reasons Donut Chart
    reasons = filtered_data['reason_start'].value_counts().reset_index()
    reasons.columns = ['reason_start', 'count']
    reason_donut_chart = px.pie(reasons, values='count', names='reason_start', template='plotly_dark', hole=0.3, color_discrete_sequence=px.colors.sequential.Emrld)
    reason_donut_chart.update_traces(textinfo='none')
    reason_donut_chart.update_layout(title='Playback Reasons')

    # Platform Usage Donut Chart
    platform_usage = filtered_data['platform'].value_counts().reset_index()
    platform_usage.columns = ['platform', 'count']
    platform_donut_chart = px.pie(platform_usage, values='count', names='platform', template='plotly_dark', hole=0.3, color_discrete_sequence=['#28a745'])
    platform_donut_chart.update_traces(textinfo='none')
    platform_donut_chart.update_layout(title='Platform Usage')

    # Generate Word Cloud for Top Tracks
    top_tracks_names = ' '.join(filtered_data['track_name'].value_counts().head(50).index)
    wordcloud = WordCloud(colormap='viridis', height=220).generate(top_tracks_names)
    

    # Convert wordcloud to base64 image for Dash rendering
    img_stream = BytesIO()
    wordcloud.to_image().save(img_stream, format='PNG')
    img_stream.seek(0)
    img_data = base64.b64encode(img_stream.read()).decode()

    # Data URL for the word cloud image
    word_cloud_url = f"data:image/png;base64,{img_data}"

    return trend_chart, artist_chart, reason_donut_chart, platform_donut_chart, word_cloud_url

if __name__ == '__main__':
    app.run_server()
