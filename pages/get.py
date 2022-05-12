import json
import os
from hoshino.config import MODULES_ON
from hoshino import config
import numpy as np
import nonebot
import markdown
import codecs

bot = nonebot.get_bot()

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

def load_config(inbuilt_file_var):
    filename = os.path.join(os.path.dirname(inbuilt_file_var), 'service.json')
    with open(filename, encoding='utf8') as f:
        config = json.load(f)
        return config

config = load_config(__file__)
Module = set_default(MODULES_ON)
config['MODULES'] = Module
config_file = os.path.join(os.path.dirname(__file__), 'service.json')
with open(config_file, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False)

routes = []
for Module_single in Module:
    routes.append(f'/autohelp/{Module_single}')

for route in routes:
    @bot.server_app.route(route, endpoint = route)
    async def help(route_edit=route):
        path = route_edit.replace('/autohelp/','')
        username = f'{path}/userreadme.md'
        name = f'{path}/readme.md'
        name2 = f'{path}/README.md'
        name3 = f'{path}/README.MD'
        userfilename = os.path.join(os.path.dirname(os.path.dirname(__file__)), username)
        filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), name)
        filename2 = os.path.join(os.path.dirname(os.path.dirname(__file__)), name2)
        filename3 = os.path.join(os.path.dirname(os.path.dirname(__file__)), name3)
        try:
            input_file = codecs.open(userfilename, mode="r", encoding="utf-8")
        except: 
            try:
                input_file = codecs.open(filename, mode="r", encoding="utf-8")
            except:
                try:
                    input_file = codecs.open(filename2, mode="r", encoding="utf-8")
                except:
                    try:
                        input_file = codecs.open(filename3, mode="r", encoding="utf-8")
                    except:
                        return 'None'
        text = input_file.read()
        html = markdown.markdown(text, extensions=['markdown.extensions.fenced_code', 'markdown.extensions.tables'])
        return html

@bot.server_app.route('/autohelp/jsondata')
async def jsondata():
    return config
