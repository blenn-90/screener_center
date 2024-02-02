import requests
import src.utilities.static_data_unsharable as static_data_unsharable 

def send_message(bot_message):
    bot_token = static_data_unsharable.telegram_bot
    chat_id = "143817638"
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id='+chat_id +'&parse_mode=MarkdownV2&text=' + bot_message
    print(send_text)
    response = requests.get(send_text)
    print(response.json()) 
    return response.json()

send_message("ffd")