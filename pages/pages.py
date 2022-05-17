import os
import nonebot
from quart import Blueprint, render_template, Markup
from hoshino import Service, priv, config
from hoshino.config import MODULES_ON
from pathlib import Path
import markdown
import json

public_address = "127.0.0.1"#修改为服务器公网ip
SERVICE_MODE = False # true为服务模式，即读取插件名字和插件help
# false则读取modules文件夹下插件名字以及对应的userreadme或readme


sv_help = '''
- [帮助] 帮助页面的网页端
'''.strip()

sv = Service(
    name = '网页端',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '通用', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助网页端"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    


work_env = Path(os.path.dirname(__file__))
homework_folder = work_env.joinpath('img')
static_folder = work_env.joinpath('static')
hp = Blueprint('hp',__name__,template_folder='templates',static_folder=static_folder)
bot = nonebot.get_bot()
app = bot.server_app
sv.logger.info(homework_folder)

service_help = None


def load_black_list():
    '''获取不想被放出帮助的插件列表'''
    _path = os.path.join(os.path.dirname(__file__), 'black.json')
    if os.path.exists(_path):
        with open(_path, "r") as f:
            black = json.load(f)
        return set(black)
    else:
        sv.logger.warning(f"black.json 文件不存在")


def get_readme_path(module_name):
    '''获取module的帮助路径'''
    READMEs = ["userreadme.md", "readme.md",
               "README.md", "README.MD", "readme.MD"]
    base = os.path.join(os.getcwd(), 'hoshino', 'modules', module_name)
    print(base)
    readme_path = None
    for readme in READMEs:
        file_path = os.path.join(base, readme)
        if os.path.exists(file_path):
            readme_path = file_path
            break
    return readme_path


def load_modules_readme():
    '''获取module的帮助'''
    svs = [] 
    black = load_black_list()
    for module in MODULES_ON:
        if module in black:
            continue
        readme_path = get_readme_path(module)
        help = "None"
        if readme_path is not None:
            with open(readme_path, "r") as f:
                help = f.read()
        svs.append({"name": module, "help": help})
    return svs

def load_services_readme():
    '''获取服务的帮助'''
    services = Service.get_loaded_services()
    black = load_black_list()
    svs = []
    for _, sv in services.items():
        if sv.name in black:
            continue
        help = "None" if sv.help is None else sv.help
        svs.append({"name": sv.name, "help": help})
    return svs

def init():
    '''帮助文案初始化'''
    global service_help

    if SERVICE_MODE:
        services = load_services_readme()
    else:
        services = load_modules_readme()
    services.sort(key=lambda data:data["name"])
    service_help = []
    id = 0
    for sv in services:
        # Markup防止html渲染时html的tag符号被转移
        html = Markup(markdown.markdown(sv["help"], extensions=[
                      'markdown.extensions.fenced_code', 'markdown.extensions.tables']))
        service_help.append({"id": id, "name": sv["name"], "help": html})
        id += 1


@hp.route('/bot/help')
async def index():
    global service_help
    if service_help is None:
        init()
    return await render_template('help.html', services=service_help)

@sv.on_fullmatch("帮助网页版",only_to_me=False)
async def get_uploader_url(bot, ev):
    cfg = config.__bot__
    await bot.send(ev,f'http://{public_address}:{cfg.PORT}/bot/help')
