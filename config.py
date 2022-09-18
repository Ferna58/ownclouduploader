import os
import ProxyCloud

#Bot Config
BOT_TOKEN = os.environ.get('bot_token')

#Storage Config
BASE_ROOT_PATH = 'root/'

#Account Config
OWN_USER = os.environ.get('account_user')
OWN_PASSWORD = os.environ.get('account_password')

# Proxy Config
PROXY_IP:str = None
PROXY_PORT:int = None
PROXY_OBJ = ProxyCloud.parse(os.environ.get('proxy_enc'))
if PROXY_OBJ:
    PROXY_IP = PROXY_OBJ.ip
    PROXY_PORT = PROXY_OBJ.port
