from flask import Flask, render_template, request, Response
from waitress import serve
import src.screener.main as screener
from flask_paginate import Pagination, get_page_parameter

app = Flask(__name__)
print("----- WEB APP | START -----")
#label position table
headings = ("Pair", "Ema Cross Value", "Current Value", "Current Ema Distance", "Special Exit (x5 SEma)")
#label updates table
headings_signal = ("Pair", "Type", "Value",  "Fast Ema (72)", "Slow Ema (256)", "ATR", "Hardstop (x4 atr)", "Born at cycle")
#label updates table
headings_portfolio = ("Date","Pair", "Exchange", "Status", "Buy Price", "Market Price", "Close Price", "Risk", "Result", "Fee")
#read data from folder
data = screener.get_data()
#calculate positions
positions = screener.get_positions(data)
#calculate updates
updates = screener.get_updates(data)
#calculate portfolio
portfolio = screener.get_portfolio()
#calculate dashboard data
dashboard_data = screener.get_dashboard_data(data, positions)
print("-----  WEB APP | END -----")

#dashboard
@app.route('/')
@app.route('/index')
def index():
    menu = [{'label':'Dashboard','class':'active bg-gradient-primary', 'href':'/index', 'icon':'dashboard'}, 
        {'label':'Open Trades','class':'', 'href':'/positions', 'icon':'receipt_long'}, 
        {'label':'Last Updates','class':'', 'href':'/updates', 'icon':'notifications'}]

    return render_template('index.html',
                            menu = menu,
                            dashboard_data = dashboard_data
                            )
#position page
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
    return render_template('positions.html', 
                            title = "Positions",
                            headings = headings, 
                            pagination = pagination, 
                            items_pagination=position_items_pagination,
                            menu = menu
                            )
#updates page
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
#portfolio page
@app.route('/portfolio')
def portfolio_def():
    menu = [{'label':'Dashboard','class':'', 'href':'/index', 'icon':'dashboard'}, 
        {'label':'Open Trades','class':'', 'href':'/positions', 'icon':'receipt_long'}, 
        {'label':'Last Updates','class':'', 'href':'/updates', 'icon':'notifications'}]
    
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page 

    items_pagination = portfolio["composition"][offset:offset+per_page] 
    total = len(portfolio) 
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=total) 
    return render_template('portfolio.html',
                            headings_portfolio = headings_portfolio, 
                            pagination = pagination, 
                            items_pagination=items_pagination,
                            menu = menu,
                            starting_balance = portfolio["balance"],
                            current_balance = portfolio["current_balance"],
                            open_trades = portfolio["open_trades"],
                            closed_trades = portfolio["closed_trades"],
                            total_open_risk = portfolio["total_open_risk"],
                            realized = portfolio["realized"],
                            unrealized = portfolio["unrealized"],
                            realized_dollar = portfolio["realized_dollar"],
                            unrealized_dollar = portfolio["unrealized_dollar"]
                            )

#download tradingview list in position page
@app.route('/export_tradingview')
def download():
    final_txt = "" 
    for pair in positions:
        final_txt = final_txt + "KUCOIN:"+ pair['pair'] + "USDT,"

    return Response(
        final_txt,
        mimetype='text/plain',
        headers={'Content-disposition': 'attachment; filename=export_tradingview.txt'})

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)