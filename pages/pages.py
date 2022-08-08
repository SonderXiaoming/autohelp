import os
import nonebot
from quart import Blueprint, render_template, Markup
from hoshino import Service, priv, config
from hoshino.config import MODULES_ON
from pathlib import Path
import markdown
import json
import datetime

public_address = "127.0.0.1"  # 修改为服务器公网ip
SERVICE_MODE = 2  # 1为服务模式，即读取插件名字和插件help
# 2为读取bundle模式
# 0则读取modules文件夹下插件名字以及对应的user readme或readme
INVISIBLE = True  # SERVICE_MODE下隐藏visible属性为false的service

sv_help = '''
- [帮助] 帮助页面的网页端
- [设置最新服务]
'''.strip()

sv = Service(
    name='网页端',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.ADMIN,  # 管理权限
    visible=True,  # 是否可见
    enable_on_default=True,  # 是否默认启用
    bundle='通用',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_fullmatch(["帮助网页端"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


work_env = Path(os.path.dirname(__file__))
homework_folder = work_env.joinpath('img')
static_folder = work_env.joinpath('static')
hp = Blueprint('hp', __name__, template_folder='templates', static_folder=static_folder)
bot = nonebot.get_bot()
app = bot.server_app
sv.logger.info(homework_folder)

service_help = None
latest_help = None

@hp.route('/bot/help')
async def index():
    global service_help
    if service_help is None:
        init()
        if SERVICE_MODE == 2:
            check_latest()
    return await render_template('help.html', services=service_help, SERVICE_MODE=SERVICE_MODE, latest=latest_help)


@sv.on_fullmatch("帮助网页版", only_to_me=False)
async def get_uploader_url(bot, ev):
    cfg = config.__bot__
    await bot.send(ev, f'http://{public_address}:{cfg.PORT}/bot/help')


def load_from_json(_path):
    '''读取json'''
    data = None
    if os.path.exists(_path):
        with open(_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        sv.logger.warning(f"{_path} 文件不存在")
    return data


def load_black_list():
    '''获取不想被放出帮助的插件列表'''
    _path = os.path.join(os.path.dirname(__file__), 'black.json')
    black = load_from_json(_path)
    return set() if black is None else set(black)


def load_replace_list():
    '''获取替换名字的插件列表'''
    _path = os.path.join(os.path.dirname(__file__), 'replace.json')
    replace = load_from_json(_path)
    return dict() if replace is None else replace


def get_readme_path(module_name):
    '''获取module的帮助路径'''
    READMEs = ["userreadme.md", "readme.md",
               "README.md", "README.MD", "readme.MD"]
    base = os.path.join(os.getcwd(), 'hoshino', 'modules', module_name)
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
    replace = load_replace_list()
    for module in MODULES_ON:
        if module in black:
            continue
        readme_path = get_readme_path(module)
        help = "None"
        if readme_path is not None:
            with open(readme_path, "r", encoding="utf-8") as f:
                help = f.read()
        name = module if module not in replace.keys() else replace[module]
        svs.append({"name": name, "help": help})
    return svs


def load_services_readme():
    '''获取服务的帮助'''
    svs = []
    black = load_black_list()
    replace = load_replace_list()
    services = Service.get_loaded_services()
    for _, sv in services.items():
        if sv.name in black:
            continue
        if INVISIBLE and sv.visible == False:
            continue
        help = "None" if sv.help is None else sv.help
        name = sv.name if sv.name not in replace.keys() else replace[sv.name]
        svs.append({"name": name, "help": help})
    return svs


def load_bundle_readme():
    """从bundle获取帮助"""
    bundles = Service.get_bundles()
    # services = Service.get_loaded_services()
    legal_bundle = ["订阅", "查询", "会战", "娱乐", "通用"]
    illegal_bundle = []
    for i in bundles:
        if i not in legal_bundle:
            for j in bundles[i]:
                bundles["娱乐"].append(j)
            illegal_bundle.append(i)
    for each in illegal_bundle:
        del bundles[each]
    data = []
    for i in bundles:
        helps = {
            "bundle": i,
            "services": []
        }
        for j in bundles[i]:
            if INVISIBLE and not j.visible:
                continue
            helping = "None" if j.help is None else j.help
            helps["services"].append(
                {"name": j.name, "help": helping}
            )
        data.append(helps)

    return data


def init():
    """帮助文案初始化"""
    global service_help
    service_help = []
    ids = 0

    if SERVICE_MODE:
        services = load_services_readme()
        services.sort(key=lambda data: data["name"])
        for sv2 in services:
            # Markup防止html渲染时html的tag符号被转移
            html = Markup(markdown.markdown(sv2["help"], extensions=[
                'markdown.extensions.fenced_code', 'markdown.extensions.tables']))
            service_help.append({"id": ids, "name": sv2["name"], "help": html})
            ids += 1
    elif SERVICE_MODE == 2:
        bid = 0
        bundles = load_bundle_readme()
        for i in bundles:
            data = {
                "bid": bid,
                "bundle": i["bundle"],
                "services": []
            }
            for j in i["services"]:
                html = Markup(markdown.markdown(j["help"], extensions=[
                    'markdown.extensions.fenced_code', 'markdown.extensions.tables']))
                data["services"].append(
                    {
                        "id": ids,
                        "name": j["name"],
                        "help": html
                    }
                )
                ids += 1
            if not len(data["services"]) == 0:
                service_help.append(data)
                bid += 1
    else:
        services = load_modules_readme()
        services.sort(key=lambda data: data["name"])
        for sv2 in services:
            # Markup防止html渲染时html的tag符号被转移
            html = Markup(markdown.markdown(sv2["help"], extensions=[
                'markdown.extensions.fenced_code', 'markdown.extensions.tables']))
            service_help.append({"id": ids, "name": sv2["name"], "help": html})
            ids += 1

# noinspection PyTypeChecker
# noinspection PyUnresolvedReferences
def check_latest():
    global latest_help
    global service_help
    latest_path = os.path.join(work_env, "latest.json")
    if os.path.exists(latest_path):
        try:
            latest = json.load(open(latest_path, encoding="utf-8"))
        except json.decoder.JSONDecodeError:
            return
    else:
        return
    bid = 0
    data = {
        "bid": 0,
        "bundle": "最新功能",
        "services": []
    }
    for i in latest:
        for j in service_help:
            if j["bid"] > bid:
                bid = j["bid"]
            for k in j["services"]:
                if k["name"] == i["service"]:
                    now = datetime.datetime.now()
                    set_time = datetime.datetime.strptime(i["time"], "%Y-%m-%d")
                    delta = (now - set_time).days
                    if delta <= 7:
                        data["services"].append(k)
    if not len(data["services"]) == 0:
        latest_help = data


@sv.on_prefix("设置最新服务")
async def set_latest(bot, ev):
    args = ev.message.extract_plain_text()
    services = Service.get_loaded_services()
    if args not in services:
        await bot.finish(ev, "不存在此服务")
    latest_path = os.path.join(work_env, "latest.json")
    if os.path.exists(latest_path):
        try:
            latest = json.load(open(latest_path, encoding="utf-8"))
        except json.decoder.JSONDecodeError:
            latest = []
    else:
        latest = []
    now = datetime.datetime.now().strftime("%Y-%m-%d")

    exists = False
    for each in latest:
        if each["service"] == args:
            each["time"] = now
            exists = True
    if not exists:
        single = {
            "service": args,
            "time": now
        }
        latest.append(single)
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(latest, indent=2, ensure_ascii=False))
    await bot.send(ev, "设置完成")
    check_latest()
