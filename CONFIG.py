import os

class CONFIG:
    IVM_DB_URI =  "sqlite:///data.db"

    IVM_SECRET_KEY = "asdfjiaoksdfiwmsdfjm"
    IVM_ALGORITHM = "HS256"

    IVM_USERNAME = "admin"
    IVM_PASSWORD = "998877"

    # IVM_ORIGINS = ["*"]
    

# ENV 变量覆盖
attr: str
for attr in CONFIG.__dict__:
    if attr.startswith("__"):
        # 魔法属性, 跳过
        continue
    else:
        if attr in os.environ:
            if attr == 'IVM_ORIGINS':
                setattr(CONFIG, attr, os.environ[attr].split(','))
            else:
                setattr(CONFIG, attr, os.environ[attr])
