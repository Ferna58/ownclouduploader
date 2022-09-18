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
#PROXY_OBJ = ProxyCloud.parse(os.environ.get('proxy_enc'))
PROXY_OBJ = ProxyCloud.parse('socks5://KHDEKJYEJJJKGIYDJHGFGEYHKKFJEGRIDHLIDILD')

#SET In DEBUG
#BOT_TOKEN = '5650727294:AAE4-x3fzPWLeIopQ9b4PWjOYza_U8shJRE'
#OWN_USER = 'ljgaliano'
#OWN_PASSWORD = 'Pelusa1234/**'