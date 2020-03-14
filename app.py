from flask import Flask, render_template, request
import urllib.request
import plotly
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json

from get_papers import MakeJson
from networkgraph import createGraph

app = Flask(__name__, static_url_path='/static')

papers = {}

@app.route('/')
def index():
    return render_template('/index.html')

@app.route('/graph', methods = ['POST', 'GET'])
def display_graph():
    if request.method == 'POST':
        id = request.form['id']
        MakeJson(id)
        createGraph()

        return render_template('network.html')

if __name__ == '__main__':
    app.run(debug=True) 