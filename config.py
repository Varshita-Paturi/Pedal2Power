import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'pedalpower-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pedalpower.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
