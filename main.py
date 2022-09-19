from datetime import datetime

from pyobigram.client import ObigramClient,inlineKeyboardMarkup,inlineKeyboardButton
from pyobigram.utils import get_file_size,sizeof_fmt,get_url_file_name,createID
from pydownloader.downloader import Downloader

import pyobigram
import pydownloader
import zipfile
import ownclient

import os
import time
import config

def send_root(update,bot,message,cloud=False):
    listdir = os.listdir(config.BASE_ROOT_PATH)
    reply = '📄 Root 📄\n\n'
    i=-1
    if cloud:
        listdir = ownclient.getRootStacic(config.OWN_USER, config.OWN_PASSWORD, config.PROXY_OBJ)
        for item in listdir:
                i+=1
                try:
                    fname = item
                    fsize = ownclient.getFileSizeStatic(config.OWN_USER, config.OWN_PASSWORD,listdir[item]+'?downloadStartSecret', config.PROXY_OBJ)
                    prettyfsize = sizeof_fmt(fsize)
                    reply += str(i) + ' - ' + fname + ' ' + prettyfsize + '\n'
                except:pass
        pass
    else:
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

LISTENING = {}


def progress(dl, filename, currentBits, totalBits, speed, totaltime, args,compresed=False):
    try:
        bot = args[0]
        message = args[1]

        def text_progres(index, max):
            try:
                if max < 1:
                    max += 1
                porcent = index / max
                porcent *= 100
                porcent = round(porcent)
                make_text = ''
                index_make = 1
                make_text += '\n'
                while (index_make < 15):
                    if porcent >= index_make * 5:
                        make_text += '▰'
                    else:
                        make_text += '▱'
                    index_make += 1
                make_text += ''
                return make_text
            except Exception as ex:
                return ''

        def porcent(index, max):
            porcent = index / max
            porcent *= 100
            porcent = round(porcent)
            return porcent

        if compresed:
            msg = '🧰 Comprimiendo Archivo....\n'
            msg += '📁 Archivo: ' + filename + ''
            msg += text_progres(currentBits, totalBits) + ' ' + str(porcent(currentBits, totalBits)) + '%\n' + '\n'
            msg += '☑ Total: ' + sizeof_fmt(totalBits) + '\n'
            msg += '🌀 Procesado: ' + sizeof_fmt(currentBits) + '\n'
            bot.editMessageText(message, msg)
        else:
            msg = '📡 Descargando Archivo....\n'
            msg += '📁 Archivo: ' + filename + ''
            msg += text_progres(currentBits, totalBits) + ' ' + str(porcent(currentBits, totalBits)) + '%\n' + '\n'
            msg += '☑ Total: ' + sizeof_fmt(totalBits) + '\n'
            msg += '📥 Descargado: ' + sizeof_fmt(currentBits) + '\n'
            msg += '🚀 Velocidad: ' + sizeof_fmt(speed) + '/s\n'
            msg += '⏱ Tiempo de Descarga: ' + str(time.strftime('%H:%M:%S', time.gmtime(totaltime))) + 's\n\n'
            bot.editMessageText(message, msg)

    except Exception as ex:
        print(str(ex))

def progresscompress(dl, file_name, current_bytes, total_bytes, args):progress(dl,file_name,current_bytes,total_bytes,0,0,args,compresed=True)

def onmessage(update,bot:ObigramClient):
    text = update.message.text
    reply_subject_text = ''
    reply_subject_file = ''

    message = None

    if '/setenv' in text:
        key = None
        value = None
        try:
            key = str(text).split(' ')[1]
            value = str(text).split(' ')[2]
            os.environ[key] = value
            bot.sendMessage(update.message.chat.id, '✅Variable De Entorno Seteada✅')
        except Exception as ex:
            pass

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

    if '/listenup' in text:
        listenid = createID(12)
        LISTENING[listenid] = False
        listenmarkup = inlineKeyboardMarkup(
            r1=[inlineKeyboardButton(text='💢Canelar Tarea💢',callback_data='/cancel '+listenid)])
        index = None
        range = None
        try:
            index = int(str(text).split(' ')[1])
            range = int(str(text).split(' ')[2])
        except:
            pass
        if  range:
            message = bot.sendMessage(update.message.chat.id, f'🧩Escuchando Cambios...',reply_markup=listenmarkup)
            lastfile = ''
            listdir = os.listdir(config.BASE_ROOT_PATH)
            while index <= range and LISTENING[listenid] == False:
                file = config.BASE_ROOT_PATH + listdir[index]
                fname = listdir[index]
                bot.editMessageText(message, f'🧩Listen Uploader For '+fname,reply_markup=listenmarkup)
                #wait for file no in root
                waitupdate = True
                while waitupdate:
                    if LISTENING[listenid] == True: break
                    files = ownclient.getRootStacic(config.OWN_USER, config.OWN_PASSWORD, config.PROXY_OBJ)
                    if lastfile in files:
                        waitupdate = True
                    else:
                        waitupdate = False
                if LISTENING[listenid] == True:
                    LISTENING.pop(listenid)
                    break
                lastfile = listdir[index]
                # upload file to owncloud
                if file:
                    data = ownclient.uploadstatic(config.OWN_USER, config.OWN_PASSWORD, file, config.PROXY_OBJ)
                    if data:
                        reply = '💚' + str(listdir[index]) + ' Subido💚\n'
                        reply += '<a href="' + data['url'] + '">🔗Link Descarga🔗</a>\n'
                        reply += '🪆Cuenta🪆\n'
                        reply += '🏮Usuario: ' + config.OWN_USER + '\n'
                        reply += '🏮Contraseña: ' + config.OWN_PASSWORD + '\n'
                        bot.sendMessage(message.chat.id, reply, parse_mode='html')
                    else:
                        bot.sendMessage(message.chat.id, '⭕Error No Se Subio⭕', parse_mode='html')
                index += 1
            bot.editMessageText(message, f'🧩Listen Uploader Finish ✅')

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
                    data = ownclient.uploadstatic(config.OWN_USER,config.OWN_PASSWORD,file, config.PROXY_OBJ)
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
                        data = ownclient.uploadstatic(config.OWN_USER, config.OWN_PASSWORD, file, config.PROXY_OBJ)
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
            filezise = get_file_size(ffullpath)
            multifile = zipfile.MultiFile(zipname, 1024 * 1024 * sizemb,filezise,progressfunc=progresscompress,args=(bot,message))
            zip = zipfile.ZipFile(multifile, mode='w', compression=zipfile.ZIP_DEFLATED)
            zip.write(ffullpath)
            zip.close()
            multifile.close()
            send_root(update,bot,message)

    if 'http' in text:
        message = bot.sendMessage(update.message.chat.id, '⏳Procesando...')
        down = Downloader(config.BASE_ROOT_PATH)
        file = down.download_url(text,progressfunc=progress,args=(bot,message))
        reply = '💚Archivo Descargado💚\n'
        reply += '📄Nombre: ' + file + '\n'
        reply += '🗳Tamaño: ' + str(sizeof_fmt(get_file_size(file))) + '\n'
        bot.editMessageText(message,reply)
        send_root(update,bot,None)
        pass

    if '/files' in text:send_root(update,bot,None,True)
    if '/share' in text:
        index = None
        password = ''
        try:
            index = int(str(text).split(' ')[1])
            password = str(text).split(' ')[2]
        except:
            pass
        if index!=None:
            root = ownclient.getRootStacic(config.OWN_USER, config.OWN_PASSWORD, config.PROXY_OBJ)
            filepath = ''
            i=-1
            for item in root:
                i+=1
                if i==index:
                    filepath = item
                    break
            shareurl = ownclient.shareStacic(config.OWN_USER, config.OWN_PASSWORD,filepath,password, config.PROXY_OBJ)
            if shareurl:
                reply = f'🔗{filepath} Compratido🔗'
                reply_markup = inlineKeyboardMarkup(
                    r1=[inlineKeyboardButton('🖇Enlace Compartido🖇',url=shareurl)],
                    r2=[inlineKeyboardButton('📛Eliminar Archivo📛',callback_data='/delete '+filepath)]
                )
                bot.sendMessage(update.message.chat.id,reply,reply_markup=reply_markup)

    print('Finished Procesed Message!')

def cancellisten(update,bot:ObigramClient):
    try:
        cmd = str(update.data).split(' ')
        listenid = cmd[0]
        LISTENING[listenid] = True
    except:pass
    pass
def delete(update,bot:ObigramClient):
    try:
        pathfile = str(update.data)
        ownclient.deleteStacic(config.OWN_USER, config.OWN_PASSWORD,pathfile, config.PROXY_OBJ)
        bot.editMessageText(update.message,f'🛑{pathfile} Eliminado🛑')
    except:pass
    pass

def main():
    print('Bot Started!')
    bot = ObigramClient(config.BOT_TOKEN)
    bot.onMessage(onmessage)
    bot.onCallbackData('/cancel ',cancellisten)
    bot.onCallbackData('/delete ',delete)
    bot.run()

if __name__ == '__main__':
    main()
