import os

class CONFIG:
    DB_URI =  "sqlite:///data.db"

    SECRET_KEY = os.urandom(64)
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS = 120

    UI_USERNAME = "admin"
    UI_PASSWORD = "998877"
    

# ENV 变量覆盖
attr: str
for attr in CONFIG.__dict__:
    if attr.startswith("__"):
        # 魔法属性, 跳过
        continue
    else:
        if attr in os.environ:
            setattr(CONFIG, attr, os.environ[attr])
