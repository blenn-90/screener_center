from flask import Flask, render_template, request
from waitress import serve

app = Flask(__name__)

headings = ("Pair", "Status", "Duration", "Entry", "Current", "Ema Distance")
data = (
    ("BTCUSDT", "Open", "14 Days", "24214", "41020", "1%"),
    ("ETHUSDT", "Open", "35 Days", "1444", "23444", "1.6%"),
    ("ADAUSDT", "Open", "134 Days", "0.353", "0.934", "13%"),
    ("XRPUSDT", "Open", "13 Days", "1", "2.53", "32%"),
    ("ETCUSDT", "Open", "4 Days", "0.15", "144", "3%")
)

headings_signal = ("Pair", "Signal", "Date", "Entry", "Stop-Loss")
data_signal = (
    ("BTCUSDT", "Bullish-Cross", "01/01/2024 04:00", "41444", "39844"),
    ("PIPEUSDT", "Bearish-Cross", "01/01/2024 04:00", "2", "1.56"),
    ("SOLUSDT", "Bullish-Cross", "01/01/2024 00:00", "7", "6"),
    ("ORDIUSDT", "Bullish-Cross", "01/01/2024 00:00", "22", "20"),
)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', headings = headings, data = data, headings_signal = headings_signal, data_signal = data_signal)

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)