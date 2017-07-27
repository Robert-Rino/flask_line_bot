from flask import request
from flask_restful import Resource

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

class Bassic(Resource):
    def post(event_obj):
        # signature = request.headers['X-Line-Signature']
        print(event_obj)
        return  200


    #     try:
    #         handler.handle(body, signature)
    #     except InvalidSignatureError:
    #         return {'message': 'handler error'}, 400
    #
    #     return 'OK'
    #
    # @staticmethod
    # @handler.add(MessageEvent, message=TextMessage)
    # def handle_message(event):
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=event.message.text))
