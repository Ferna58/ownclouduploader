from pyobigram.client import ObigramClient
from pyobigram.utils import get_file_size,sizeof_fmt,get_url_file_name
from pydownloader.downloader import Downloader

import pyobigram
import pydownloader
import zipfile
import ownclient

import os
import config

def send_root(update,bot,message):
    listdir = os.listdir(config.BASE_ROOT_PATH)
    reply = '📄 Root 📄\n\n'
    i=-1
    for item in listdir:
            i+=1
            fname = item
            fsize = get_file_size(config.BASE_ROOT_PATH + item)
            prettyfsize = sizeof_fmt(fsize)
            reply += str(i) + ' - ' + fname + ' ' + prettyfsize + '\n'
    if message:
        bot.editMessageText(message,reply)
    else:
        bot.sendMessage(update.message.chat.id, reply)

def onmessage(update,bot:ObigramClient):
    text = update.message.text
    reply_subject_text = ''
    reply_subject_file = ''

    message = None

    if '/start' in text:
        reply = '<a href="https://github.com/ObisoftDev">👋 OwnCloudUploader 👋</a>\n\n'
        reply += 'Bot Para Descargar Archivos Desde Internet Directo A Tu OwnCloudUci'
        message = bot.sendMessage(update.message.chat.id,reply,parse_mode='html')
        pass

    if '/ls' in text: send_root(update,bot,message)

    if '/rm' in text:
        index = None
        range = None
        try:
            index = int(str(text).split(' ')[1])
            range = int(str(text).split(' ')[2])
        except:
            pass
        if index != None:
            listdir = os.listdir(config.BASE_ROOT_PATH)
            if range == None:
                rmfile = config.BASE_ROOT_PATH + listdir[index]
                os.unlink(rmfile)
            else:
                while index <= range:
                    rmfile = config.BASE_ROOT_PATH + listdir[index]
                    os.unlink(rmfile)
                    index += 1
        send_root(update,bot,message)

    if '/upload' in text:
        index = None
        range = None
        try:
            index = int(str(text).split(' ')[1])
            range = int(str(text).split(' ')[2])
        except:
            pass
        if index != None:
            listdir = os.listdir(config.BASE_ROOT_PATH)
            if range == None:
                message = bot.sendMessage(update.message.chat.id,f'📤Subiendo {listdir[index]}...')
                file = config.BASE_ROOT_PATH + listdir[index]
                #upload file to owncloud
                if file:
                    data = ownclient.uploadstatic(config.OWN_USER,config.OWN_PASSWORD,file,config.PROXY_IP,config.PROXY_PORT)
                    if data:
                        reply = '💚'+str(listdir[index])+' Subido💚\n'
                        reply += '<a href="'+data['url']+'">🔗Link Descarga🔗</a>\n'
                        reply += '🪆Cuenta🪆\n'
                        reply += '🏮Usuario: '+config.OWN_USER+'\n'
                        reply += '🏮Contraseña: '+config.OWN_PASSWORD+'\n'
                        bot.editMessageText(message,reply, parse_mode='html')
                    else:
                        bot.editMessageText(message, '⭕Error No Se Subio⭕', parse_mode='html')
            else:
                message = bot.sendMessage(update.message.chat.id,f'📤Subiendo Archivos...')
                while index <= range:
                    file = config.BASE_ROOT_PATH + listdir[index]
                    fname = listdir[index]
                    #upload file to owncloud
                    if file:
                        data = ownclient.uploadstatic(config.OWN_USER, config.OWN_PASSWORD, file,config.PROXY_IP,config.PROXY_PORT)
                        if data:
                            reply = '💚' + str(listdir[index]) + ' Subido💚\n'
                            reply += '<a href="' + data['url'] + '">🔗Link Descarga🔗</a>\n'
                            reply += '🪆Cuenta🪆\n'
                            reply += '🏮Usuario: ' + config.OWN_USER + '\n'
                            reply += '🏮Contraseña: ' + config.OWN_PASSWORD + '\n'
                            bot.sendMessage(message.chat.id, reply,parse_mode='html')
                        else:
                            bot.sendMessage(message.chat.id, '⭕Error No Se Subio⭕', parse_mode='html')
                    index += 1
        send_root(update,bot,None)

    if 'zip' in text:
        index = None
        sizemb = 200
        try:
            index = int(str(text).split(' ')[1])
            sizemb = int(str(text).split(' ')[2])
        except:
            pass
        if index != None:
            listdir = os.listdir(config.BASE_ROOT_PATH)
            ffullpath = config.BASE_ROOT_PATH + listdir[index]
            message = bot.sendMessage(update.message.chat.id,f'📚Comprimiendo {listdir[index]}...')
            zipname = str(ffullpath).split('.')[0]
            multifile = zipfile.MultiFile(zipname, 1024 * 1024 * sizemb)
            zip = zipfile.ZipFile(multifile, mode='w', compression=zipfile.ZIP_DEFLATED)
            zip.write(ffullpath)
            zip.close()
            multifile.close()
            send_root(update,bot,message)

    if 'http' in text:
        down = Downloader(config.BASE_ROOT_PATH)
        file = down.download_url(text)
        reply = '💚Archivo Descargado💚\n'
        reply += '📄Nombre: ' + file + '\n'
        reply += '🗳Tamaño: ' + str(sizeof_fmt(get_file_size(file))) + '\n'
        message.reply_text(text=reply, subject=reply_subject_text)
        pass
    print('Finished Procesed Message!')

def main():
    print('Bot Started!')
    bot = ObigramClient(config.BOT_TOKEN)
    bot.onMessage(onmessage)
    bot.run()

if __name__ == '__main__':
    main()