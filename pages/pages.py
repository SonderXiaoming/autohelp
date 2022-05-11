import os
import nonebot
from quart import Blueprint,render_template
from hoshino import Service, priv, config
from pathlib import Path

public_address = "127.0.0.1"#修改为服务器公网ip


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

@hp.route('/bot/help')
async def index():
    return await render_template('help.html')

@sv.on_fullmatch("帮助网页版",only_to_me=False)
async def get_uploader_url(bot, ev):
    cfg = config.__bot__
    await bot.send(ev,f'http://{public_address}:{cfg.PORT}/bot/help')
