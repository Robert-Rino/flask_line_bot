#!/usr/bin/env python
# _*_ coding: utf-8 _*_

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
    MessageEvent, PostbackEvent, FollowEvent, UnfollowEvent,
    TextMessage, TextSendMessage, StickerSendMessage,
    LocationMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn,
    ConfirmTemplate, ImageCarouselColumn,
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
    # products = data['products']

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
                uri=product['market_url'])
        ]
    ) for product in products]
    return result

# @app.route('/image_carouse', methods=['POST'])
# def image_carouse():
#     data = request.json
#     userId = data['user_id']
#     import products as product_example
#     # products = data['products']
#     products = product_example
#
#     if len(products) == 0 :
#         return jsonify({'message': 'bad request'}), 400
#
#     else:
#         product_list = buildImageColumnsForUser(products, userId)[0:4]
#         line_bot_api.push_message(
#             userId,TemplateSendMessage(
#                 alt_text='您的專屬配件',
#                 template=CarouselTemplate(
#                 columns=[
#                     product for product in product_list
#                 ]
#                 )
#             )
#         )
#         return jsonify({'message' : 'ok'}), 200

def buildImageColumnsForUser(products, userId):
    result = [ImageCarouselColumn(
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

@app.route('/send_binding', methods=['POST'])
def bindLineuserTagtoouser():
    data = request.json
    userid_list = data['userid_list']

    for userid in userid_list:
        line_bot_api.push_message(
            userid,
            TemplateSendMessage(
                alt_text='打開手機看看有什麼新商品吧',
                template=ConfirmTemplate(
                text='想看看有什麼新商品嗎',
                actions=[
                    URITemplateAction(
                    label='前往賣場看看',
                    uri='https://api-rino-demo-dot-tagtoo-staging.appspot.com/v1/ad/click?u=https://www.obdesign.com.tw/&line_cid=0001&line_uid={}'.format(userid)
                    ),
                    PostbackTemplateAction(
                        label='新鮮推薦',
                        data="user_id={}&command=recommendation".format(userid),
                    ),
                ]
                )
            )

        )

    return 'ok'

@app.route('/barcode/')
@app.route('/barcode/<barcode_id>')
def barcode(barcode_id=None):
    return render_template('index.html', barcode_id=barcode_id)

@app.route('/template_example', methods=['GET'])
def template_example():
    return render_template('index.html',barcode_id='SHK1234567890')

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

# class PostbackSwitcher():
#
#     def __init__(self, postback_data):
#         self.user_id = postback_data.user_id
#         self.command = postback_data.command



@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.push_message(
        event.source.user_id,
        TemplateSendMessage(
            alt_text='打開手機看看有什麼新商品吧',
            template=ConfirmTemplate(
            text='想看看有什麼新商品嗎',
            actions=[
                URITemplateAction(
                label='前往賣場看看',
                uri='https://api-rino-demo-dot-tagtoo-staging.appspot.com/v1/ad/click?u=https://www.obdesign.com.tw/&line_cid=0001&line_uid={}'.format(userid)
                ),
                MessageTemplateAction(
                    label='message',
                    text='message text'
                )
            ]
            )
        )

    )

@handler.add(UnfollowEvent)
def handle_follow(event):
    app.logger.info("in unfollow event userId:{}".format(event.source.user_id))

@handler.default()
def default(event):
    app.logger.info("in default handler")
    return '', 200

if __name__ == '__main__':
    app.run()
