from flask import Flask, render_template, request
from waitress import serve
import src.screener.main as screener
from flask_paginate import Pagination, get_page_parameter

app = Flask(__name__)

print("----- START RETRIVING DATA -----")

headings = ("Pair", "Status", "Ema Cross Value", "Current Value", "Current Ema Distance")
headings_signal = ("Pair", "Type", "Value",  "Fast Ema", "Slow Ema", "ATR")
data = screener.get_data()
updates = screener.get_updates(data)
positions = screener.get_positions(data)

print("----- END RETRIVING DATA -----")

@app.route('/')
@app.route('/index')
def index():
    menu = [{'label':'Dashboard','class':'active bg-gradient-primary', 'href':'/index', 'icon':'dashboard'}, 
        {'label':'Open Trades','class':'', 'href':'/positions', 'icon':'receipt_long'}, 
        {'label':'Last Updates','class':'', 'href':'/updates', 'icon':'notifications'}]

    return render_template('index.html',
                            menu = menu
                            )

@app.route('/positions')
def positions_def():
    menu = [{'label':'Dashboard','class':'', 'href':'/index', 'icon':'dashboard'}, 
        {'label':'Open Trades','class':'active bg-gradient-primary', 'href':'/positions','icon':'receipt_long'}, 
        {'label':'Last Updates','class':'', 'href':'/updates', 'icon':'notifications'}]
     
    page = int(request.args.get('page', 1))
    per_page = 15
    offset = (page - 1) * per_page 

    position_items_pagination = positions[offset:offset+per_page] 
    total = len(positions) 
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=total) 
    return render_template('positions.html', title = "Positions",
                            headings = headings, 
                            pagination = pagination, 
                            items_pagination=position_items_pagination,
                            menu = menu
                            )

@app.route('/updates')
def updates_def():
    menu = [{'label':'Dashboard','class':'', 'href':'/index', 'icon':'dashboard'}, 
        {'label':'Open Trades','class':'', 'href':'/positions', 'icon':'receipt_long'}, 
        {'label':'Last Updates','class':'active bg-gradient-primary', 'href':'/updates', 'icon':'notifications'}]
    
    page = int(request.args.get('page', 1))
    per_page = 15
    offset = (page - 1) * per_page 

    items_pagination = updates[offset:offset+per_page] 
    total = len(updates) 
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=total) 
    return render_template('updates.html',
                            headings_signal = headings_signal, 
                            pagination = pagination, 
                            items_pagination=items_pagination,
                            menu = menu
                            )


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)