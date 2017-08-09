import os, time, datetime
from flask import (
    Flask, request, abort, make_response, redirect, current_app, Response, render_template
)
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, StickerSendMessage,
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
    return render_template('index.html')
    
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    header = request.headers['X-Line-Signature']
    app.logger.info("Request body: " + body)
    app.logger.info("Request header: "+ header)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'ok', 200

@app.route('/pushtest', methods=['POST'])
def push():
    # U628c4639ff5b414f53f9270d4d499dd6
    # U1417c3eb67e02734518492add042a40e
    line_bot_api.push_message('U628c4639ff5b414f53f9270d4d499dd6',
    StickerSendMessage(
    package_id='2',
    sticker_id='140'
))
    return '', 200

@app.route('/testcookie', methods=['GET'])
def cookie():
    cookie = request.cookies
    res = make_response(('create cookie'), 200)
    if 'tagtoo' not in cookie:
        res.set_cookie('tagtoo', value='rinoupdate')
    else :
        app.logger.info("Request cookie: "+ str(cookie['tagtoo']))
    return res

@app.route('/postad', methods=['POST'])
def advertisement():
    data = request.json
    userId = data['userId']
    product_list = buildProductColumnsForUser(products, userId)

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
    return 'ok', 200

def buildProductColumnsForUser(products, userId):
    result = [CarouselColumn(
        thumbnail_image_url=product['picture_url'],
        title=product['name'],
        text="$ {}".format(product['price']),
        actions=[
            URITemplateAction(
                label='前往賣場',
                uri="https://www.google.com.tw?test={}".format(userId))
        ]
    ) for product in products]
    return result

@app.route('/redirectTest', methods=['GET'])
def redirectTest():
    # print(request.args.get('name'))
    name = request.args.get('name')
    redirectSite = redirect("https://www.obdesign.com.tw?name={}".format(name))
    # response = current_app.make_response(redirectSite)
    response = Response('add cookie')
    response.set_cookie(
    key='tagtoo',
    value='rinotest',
    expires=time.time()+6*60)
    return response


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

@handler.default()
def default(event):
    app.logger.info("in default handler")
    return '', 200

if __name__ == '__main__':
    app.run()
