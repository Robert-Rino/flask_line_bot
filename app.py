# coding: utf-8
import os
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, StickerSendMessage,
    LocationMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn,
    PostbackTemplateAction, MessageTemplateAction, URIAction
)
from nomed import Nomed

from config import config

app = Flask(__name__)
app.config.from_object(config[os.environ.get('FLASK_CONFIG', 'dev')])
# app.secret_key = os.environ.get('SECRET_KEY') or'rino'

line_bot_api = LineBotApi(app.config['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(app.config['CHANNEL_SECRET'])

@app.route('/', methods=['POST', 'GET'])
def index():
    print 'request.host: {host}'.format(host=request.host)
    return 'ok'


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK', 200

@app.route('/pushtest', methods=['POST'])
def push():
    # U628c4639ff5b414f53f9270d4d499dd6
    # U1417c3eb67e02734518492add042a40e
    line_bot_api.push_message('U628c4639ff5b414f53f9270d4d499dd6',
    StickerSendMessage(
    package_id='1171546',
    sticker_id='6982069'
))
    return '', 200


@app.route('/testgeo', methods=['GET'])
def dis():
    log = request.args.get('log')
    lat = request.args.get('lat')
    print(Nomed.findByGeo(lat, log)[:5])
    return '', 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    app.logger.info("in echo message handler, event = {} ".format(event.type))
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))

@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    log = event.message.longitude
    lat = event.message.latitude
    app.logger.info("in location handler longitude = {}, latitude = {}".format(log, lat))
    store_list = Nomed.findByGeo(lat, log)
    for line in store_list[:5]:
        print(line['url'])

    line_bot_api.reply_message(
        event.reply_token,TemplateSendMessage(
            alt_text='Carousel template',
            template=CarouselTemplate(
            columns=[
                store for store in CarouselColumnBuilder(store_list[:5])
            ]
            )
        )
    )

def CarouselColumnBuilder(stores):
    result = [CarouselColumn(
        title=store['name'].encode('utf-8'),
        text=store['address'].encode('utf-8'),
        actions=[
            URIAction(
                        label='official site',
                        uri=store['url'] if store['url'] != '' else 'https://www.facebook.com'
                    ),
            URIAction(
                        label='Nomed commends',
                        uri="https://cafenomad.tw/shop/{}".format(store['id'])
                    ),
            URIAction(
                        label='google map',
                        uri="https://maps.google.com/?q={},{}".format(store['latitude'], store['longitude'])
                    )
        ]
    ) for store in stores]
    return result

@handler.default()
def default(event):
    app.logger.info("in default handler")
    return '', 200

if __name__ == '__main__':
    app.run()
