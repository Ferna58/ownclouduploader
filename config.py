import os
import ProxyCloud

#Bot Config
BOT_TOKEN = os.environ.get('7118217205:AAHqVnayGGVAEaljlkM9x4je7giC5v0u4zo')

#Storage Config
BASE_ROOT_PATH = 'root/'

#Account Config
OWN_USER = os.environ.get('liliana.aguilar')
OWN_PASSWORD = os.environ.get('Ohsadaharuoh189!')
OWN_HOST = os.environ.get('host','https://nube.uo.edu.cu/')

# Proxy Config
PROXY_OBJ = ProxyCloud.parse(os.environ.get('proxy_enc'))
#PROXY_OBJ = ProxyCloud.parse('socks5://KHDEKJYEJJJKGIYDJHGFGEYHKKFJEGRIDHLIDILD')


if PROXY_OBJ:
    print(f"PROXY :{PROXY_OBJ.ip}:{PROXY_OBJ.port}")
