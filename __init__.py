import nonebot
from .pages import hp
app = nonebot.get_bot().server_app
app.register_blueprint(hp)