from flask import Flask, render_template, request
from waitress import serve
import src.screener.main as screener

app = Flask(__name__)


headings = ("Pair", "Status", "Ema Cross Value", "Current Value", "Current Ema Distance")
positions = screener.get_positions()

headings_signal = ("Pair", "Type", "Date", "Current Value", "ATR")
data_signal = (
)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                            positions = positions, 
                            headings = headings, 
                            headings_signal = headings_signal, 
                            data_signal = data_signal
                            )

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)