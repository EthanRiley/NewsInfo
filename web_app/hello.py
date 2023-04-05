import dash
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask, render_template
import pandas as pd

# Initialize the Flask app
app = Flask(__name__)

# Initialize the Dash app with the Flask app as its server
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash')

# Load the data
data = pd.read_csv('web_app/titanic/train.csv')
x = data['Age']
y = data['Fare']

# Create a scatter plot using Plotly
scatter_plot = {
    'data': [{
        'x': x,
        'y': y,
        'mode': 'markers',
        'marker': {'color': 'rgba(0, 0, 255, 0.5)'}
    }],
    'layout': {
        'title': 'Scatter Plot of Age vs Fare',
        'xaxis': {'title': 'Age'},
        'yaxis': {'title': 'Fare'}
    }
}

# Define the Dash app layout
dash_app.layout = html.Div([
    html.H1('Scatter Plot: Age vs Fare'),
    dcc.Graph(id='scatter-plot', figure=scatter_plot)
])

@app.route("/dash")
def dash():
    return render_template("page.html")

@app.route("/")
def homepage():
    return render_template("homepage.html")

if __name__ == "__main__":
    app.run(threaded=True)
