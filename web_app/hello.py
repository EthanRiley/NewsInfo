from flask import Flask, render_template, send_file
import matplotlib.pyplot as plt
import io
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import jinja2

app = Flask(__name__)
my_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader('templates'),
])
app.jinja_loader = my_loader


@app.route("/visualization_1")
def visualizations():
    data = pd.read_csv('titanic/train.csv')
    x = data['Age']
    y = data['Fare']
    fig, ax = plt.subplots()
    ax.scatter(x, y)
    img = io.BytesIO()
    canvas = FigureCanvas(fig)
    fig.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype='image/png')

@app.route("/")
def index():
    return render_template("page.html")

if __name__ == "__main__":
    app.run()