import os
import time
import nonebot
import re
from quart import Blueprint, render_template, Markup
from hoshino import Service, priv, config
from hoshino.config import MODULES_ON
from pathlib import Path
import markdown
import json
import datetime

public_address = "127.0.0.1"  # 修改为服务器公网ip
SERVICE_MODE = 0  # 1为服务模式，即读取插件名字和插件help
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
            check_bundle_latest()
        elif SERVICE_MODE == 1:
            check_service_latest()
        else:
            check_module_latest()
    return await render_template('help.html', services=service_help, SERVICE_MODE=SERVICE_MODE, latest=latest_help)


@sv.on_fullmatch("帮助网页版", only_to_me=False)
async def get_uploader_url(bot, ev):
    cfg = config.__bot__
    await bot.send(ev, f'http://{public_address}:{cfg.PORT}/bot/help')


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
    if SERVICE_MODE == 2:
        check_bundle_latest()
    elif SERVICE_MODE == 1:
        check_service_latest()

def load_from_json(_path):
    """读取json"""
    data = None
    if os.path.exists(_path):
        with open(_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        sv.logger.warning(f"{_path} 文件不存在")
    return data


def load_black_list():
    """获取不想被放出帮助的插件列表"""
    _path = os.path.join(os.path.dirname(__file__), 'black.json')
    black = load_from_json(_path)
    return set() if black is None else set(black)


def load_replace_list():
    """获取替换名字的插件列表"""
    _path = os.path.join(os.path.dirname(__file__), 'replace.json')
    replace = load_from_json(_path)
    return dict() if replace is None else replace


def get_readme_path(module_name):
    """获取module的帮助路径"""
    # readmes = ["userreadme.md", "readme.md",
    #            "README.md", "README.MD", "readme.MD"]
    readme_rule = re.compile(r"(?i)(user)?readme\.md")
    high_readme_rule = re.compile(r"(?i)userreadme\.md")
    base = os.path.join(os.getcwd(), 'hoshino', 'modules', module_name)
    readme_path = None
    # for readme in readmes:
    #     file_path = os.path.join(base, readme)
    #     if os.path.exists(file_path):
    #         readme_path = file_path
    #         break
    is_user_readme = False
    get_readme = True
    for module_path, _, files in os.walk(base):
        for file in files:
            if re.match(high_readme_rule, file):
                readme_path = os.path.join(module_path, file)
                is_user_readme = True
            if re.match(readme_rule, file):
                readme_path = os.path.join(module_path, file)
                get_readme = True
            if is_user_readme:
                return readme_path
        if get_readme:
            return readme_path
    return readme_path

def load_modules_readme():
    """获取module的帮助"""
    svs = []
    black = load_black_list()
    replace = load_replace_list()
    for module in config.MODULES_ON:
        if module in black:
            continue
        readme_path = get_readme_path(module)
        _help = "None"
        if readme_path is not None:
            with open(readme_path, "r", encoding="utf-8") as f:
                _help = f.read()
            name = module if module not in replace.keys() else replace[module]
            mtime = time.ctime(os.stat(readme_path).st_mtime)
            ctime = time.ctime(os.stat(readme_path).st_ctime)
            svs.append({"name": name, "help": _help, "mtime": mtime, "ctime": ctime})
    return svs


def load_services_readme():
    """获取服务的帮助"""
    svs = []
    # black = load_black_list()
    # replace = load_replace_list()
    services = Service.get_loaded_services()
    for _, sv1 in services.items():
        # if sv.name in black:
        #     continue
        if INVISIBLE and not sv1.visible:
            continue
        helping = "None" if sv1.help is None else sv1.help
        # name = sv.name if sv.name not in replace.keys() else replace[sv.name]
        svs.append({"name": sv1.name, "help": helping})
    return svs


def load_bundle_readme():
    """从bundle获取帮助"""
    bundles = Service.get_bundles()
    # services = Service.get_loaded_services()
    bundle_set = load_from_json(os.path.join(os.path.dirname(__file__), 'bundle.json'))
    legal_bundle = bundle_set["legal_bundle"]
    replace_bundle = bundle_set["replace"]
    illegal_bundle = []
    for i in bundles:
        if i in replace_bundle:
            for j in bundles[i]:
                bundles[bundle_set["replace"][i]].append(j)
            illegal_bundle.append(i)
        elif i not in legal_bundle:
            for j in bundles[i]:
                bundles[bundle_set["default_bundle"]].append(j)
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


# noinspection PyTypeChecker
# noinspection PyUnresolvedReferences
def check_module_latest():
    global latest_help
    global service_help
    data = {
        "bid": 0,
        "bundle": "最新功能",
        "services": []
    }
    for each in service_help:
        now = datetime.datetime.now()
        c = datetime.datetime.strptime(each["ctime"], "%a %b  %d %H:%M:%S %Y")
        m = datetime.datetime.strptime(each["mtime"], "%a %b  %d %H:%M:%S %Y")
        d1 = (now - c).days
        d2 = (now - m).days
        if d1 <= 7 or d2 <= 7:
            data["services"].append(each)
    if not len(data["services"]) == 0:
        latest_help = data


# noinspection PyTypeChecker
# noinspection PyUnresolvedReferences
def check_service_latest():
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
    data = {
        "bid": 0,
        "bundle": "最新功能",
        "services": []
    }
    for i in latest:
        for j in service_help:
            if j["name"] == i["service"]:
                now = datetime.datetime.now()
                set_time = datetime.datetime.strptime(i["time"], "%Y-%m-%d")
                delta = (now - set_time).days
                if delta <= 7:
                    data["services"].append(j)
    if not len(data["services"]) == 0:
        latest_help = data


def init():
    """帮助文案初始化"""
    global service_help
    service_help = []
    ids = 0

    if SERVICE_MODE == 1:
        services = load_services_readme()
        services.sort(key=lambda _data: _data["name"])
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
        services.sort(key=lambda _data: _data["name"])
        for sv2 in services:
            # Markup防止html渲染时html的tag符号被转移
            html = Markup(markdown.markdown(sv2["help"], extensions=[
                'markdown.extensions.fenced_code', 'markdown.extensions.tables']))
            service_help.append(
                {
                    "id": ids, "name": sv2["name"], "help": html,
                    "mtime": sv2["mtime"], "ctime": sv2["ctime"]
                }
            )
            ids += 1


# noinspection PyTypeChecker
# noinspection PyUnresolvedReferences
def check_bundle_latest():
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
