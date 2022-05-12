import nonebot
from .pages import ma
from .pages import hp
from .pages import tk
from .pages import ab
from .pages import sc
from .pages import js
from .pages import st
from .pages import qn
app = nonebot.get_bot().server_app
app.register_blueprint(ma)
app.register_blueprint(hp)
app.register_blueprint(tk)
app.register_blueprint(ab)
app.register_blueprint(sc)
app.register_blueprint(js)
app.register_blueprint(st)
app.register_blueprint(qn)