import os, time, datetime, requests
from flask import (
    Flask, request, abort, make_response, redirect, current_app, Response, render_template,
    jsonify
)
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, PostbackEvent,
    TextMessage, TextSendMessage, StickerSendMessage,
    LocationMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn,
    PostbackTemplateAction, MessageTemplateAction, URITemplateAction
)
from nomed import Nomed
from products import products

from config import config

app = Flask(__name__)
app.config.from_object(config[os.environ.get('FLASK_CONFIG')])
# app.secret_key = os.environ.get('SECRET_KEY') or'rino'

line_bot_api = LineBotApi(app.config['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(app.config['CHANNEL_SECRET'])

@app.route('/', methods=['GET'])
def index():
    return 'line-bot api server', 200
    # line_id = 'U628c4639ff5b414f53f9270d4d499dd6'
    # cookie = 'rino'
    # return render_template('index.html', line_id=line_id, cookie=cookie)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    header = request.headers['X-Line-Signature']
    app.logger.info("Request body: " + body)
    app.logger.info("Request signature header: "+ header)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'ok', 200


@app.route('/postad', methods=['POST'])
def advertisement():
    data = request.json
    userId = data['user_id']
    products = data['products']

    if len(products) == 0 :
        return jsonify({'message': 'bad request'}), 400

    else:
        product_list = buildProductColumnsForUser(products, userId)[0:4]
        line_bot_api.push_message(
            userId,TemplateSendMessage(
                alt_text='您的專屬配件',
                template=CarouselTemplate(
                columns=[
                    product for product in product_list
                ]
                )
            )
        )
        return jsonify({'message' : 'ok'}), 200

def buildProductColumnsForUser(products, userId):
    result = [CarouselColumn(
        thumbnail_image_url=product['picture_url'],
        title=product['name'],
        text="$ {}".format(product['price']),
        actions=[
            URITemplateAction(
                label='前往賣場',
                uri=product['target_url'])
        ]
    ) for product in products]
    return result

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
    # for line in store_list[:5]:
    #     print(line['url'])

    line_bot_api.reply_message(
        event.reply_token,TemplateSendMessage(
            alt_text='Carousel template',
            template=CarouselTemplate(
            columns=[
                store for store in buildStoreCarouselColumns(store_list[:5])
            ]
            )
        )
    )

def buildStoreCarouselColumns(stores):
    result = [CarouselColumn(
        title=store['name'],
        text=store['address'],
        actions=[
            URITemplateAction(
                label='official site',
                uri=store['url'] if store['url'] != '' else 'https://www.facebook.com'
            ),
            URITemplateAction(
                label='Nomed commends',
                uri="https://cafenomad.tw/shop/{}".format(store['id'])
            ),
            URITemplateAction(
                label='google map',
                uri="https://www.google.com.tw/maps/place/{}".format(store['address'])
            )
        ]
    ) for store in stores]
    return result

@handler.add(PostbackEvent)
def handlePostback(event):
    data = parsePostbackDataString(event.postback.data)
    print(data)
    return 'ok', 200

def parsePostbackDataString(postbackDataStirng):
    dataPairs = postbackDataStirng.split('&')
    return { dataPair.split('=')[0]: dataPair.split('=')[1] for dataPair in dataPairs}

@handler.default()
def default(event):
    app.logger.info("in default handler")
    return '', 200

if __name__ == '__main__':
    app.run()
