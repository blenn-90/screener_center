import requests
import src.utilities.static_data_unsharable as static_data_unsharable 

def send_message(bot_message):
    print("Telegram - sending notification")
    bot_token = static_data_unsharable.telegram_bot_token
    chat_id = static_data_unsharable.telegram_bot_chat_id
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id='+chat_id +'&parse_mode=MarkdownV2&text=' + bot_message
    response = requests.get(send_text)
    print(response.json())
    return response.json()