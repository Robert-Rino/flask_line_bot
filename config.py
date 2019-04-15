import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = True
    SECRET_KEY = 'rino-dev'

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'rino-dev'
    CHANNEL_ACCESS_TOKEN = "#{YOUR_ACCESS_TOKEN}"
    CHANNEL_SECRET= "#{YOUR_CHANNEL_SCRET}"

class ProductionConfig(Config):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN')
    CHANNEL_SECRET= os.environ.get('CHANNEL_SECRET')


config = {
'default': Config,
'dev': DevelopmentConfig,
'production': ProductionConfig
}
