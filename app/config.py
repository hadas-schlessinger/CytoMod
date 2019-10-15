import os

class Config(object):
    SECRET_KEY = os.urandom(16)
    DEBUG = True
    SEED = 1234
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'data_files')



