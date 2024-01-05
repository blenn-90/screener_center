from flask import Flask, render_template, request
from waitress import serve
import src.screener.main as screener

app = Flask(__name__)


headings = ("Pair", "Status", "Ema Cross Value", "Current Value", "Current Ema Distance")

data = screener.get_data()
positions = screener.get_positions(data)
updates = screener.get_updates(data)

headings_signal = ("Pair", "Type", "Value",  "Fast Ema", "Slow Ema", "ATR")

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                            positions = positions, 
                            headings = headings, 
                            headings_signal = headings_signal, 
                            updates = updates
                            )

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)