import os
import nonebot
from quart import request,session,redirect,Blueprint,url_for,render_template,jsonify,session
from nonebot.exceptions import CQHttpError
from hoshino import R, Service, priv, config
from pathlib import Path

public_address = "127.0.0.1"#修改为服务器公网ip


sv_help = '''
- [#帮助] 帮助页面的网页端
- [手册] 打开会战手册
- [主页] 浏览主页
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
ma = Blueprint('ma',__name__,template_folder='templates',static_folder=static_folder)
hp = Blueprint('hp',__name__,template_folder='templates',static_folder=static_folder)
tk = Blueprint('tk',__name__,template_folder='templates',static_folder=static_folder)
ab = Blueprint('ab',__name__,template_folder='templates',static_folder=static_folder)
sc = Blueprint('sc',__name__,template_folder='templates',static_folder=static_folder)
js = Blueprint('js',__name__,template_folder='templates',static_folder=static_folder)
st = Blueprint('st',__name__,template_folder='templates',static_folder=static_folder)
qn = Blueprint('qn',__name__,template_folder='templates',static_folder=static_folder)
bot = nonebot.get_bot()
app = bot.server_app
sv.logger.info(homework_folder)



@ma.route('/huannai/main')
async def index():
    return await render_template('main.html')

@hp.route('/huannai/help')
async def index():
    return await render_template('help.html')
    
@tk.route('/huannai/thanks')
async def index():
    return await render_template('thanks.html')

@ab.route('/huannai/about')
async def index():
    return await render_template('about.html')

@sc.route('/huannai/manual')
async def index():
    return await render_template('manual.html')

@st.route('/huannai/support')
async def index():
    return await render_template('support.html')

@qn.route('/huannai/question')
async def index():
    return await render_template('question.html')


@js.route('/huannai/404')
async def index():
    return await render_template('404.html')

@sv.on_fullmatch("主页",only_to_me=False)
async def get_uploader_url(bot, ev):
    cfg = config.__bot__
    await bot.send(ev,f'http://{public_address}:{cfg.PORT}/huannai/main')

@sv.on_fullmatch("帮助",only_to_me=False)
async def get_uploader_url(bot, ev):
    cfg = config.__bot__
    await bot.send(ev,f'http://{public_address}:{cfg.PORT}/huannai/help')
    
@sv.on_fullmatch("手册",only_to_me=False)
async def get_uploader_url(bot, ev):
    cfg = config.__bot__
    await bot.send(ev,f'http://{public_address}:{cfg.PORT}/huannai/manual')
