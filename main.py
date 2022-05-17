from fastapi import FastAPI, Depends, Query, Path, Body, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from CONFIG import CONFIG
from db import DBSession, create as db_create, drop as db_drop, fake as db_fake, Goods

from sqlalchemy import exists
from typing import Optional, List
from jose import jwt
from pydantic import BaseModel

from uvicorn import run as run_uvicorn
import sys

def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()

class GooodsType(BaseModel):
    key: int
    name: str
    quan: float
    unit: str
    mark: Optional[str]

    class Config:
        orm_mode = True

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

@app.post('/login/')
async def login(data: OAuth2PasswordRequestForm = Depends()):
    if (data.username == CONFIG.UI_USERNAME) and (data.password == CONFIG.UI_PASSWORD):
        return {
            "access_token": jwt.encode(claims={"user_name": data.username}, key=CONFIG.SECRET_KEY, algorithm=CONFIG.ALGORITHM),
            "token_type": "bearer"
        }
    else:
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post('/list/')
async def list_goods(db = Depends(get_db), _=Depends(oauth2_scheme)) -> List[GooodsType]:
    return db.query(Goods).all()

@app.post('/update/')
async def list_goods(goods: GooodsType, db = Depends(get_db), _=Depends(oauth2_scheme)) -> bool:
    try:
        indb: Goods = db.query(Goods).filter(Goods.key == goods.key).one()
    except:
        raise HTTPException(400, "没有找到该项目")
    indb.name = goods.name
    indb.mark = goods.mark
    indb.unit = goods.unit
    indb.quan = goods.quan
    db.commit()
    return True

@app.post("/del/")
async def del_goods(goods: GooodsType, db = Depends(get_db), _=Depends(oauth2_scheme)) -> bool:
    try:
        indb: Goods = db.query(Goods).filter(Goods.key == goods.key).one()
    except:
        raise HTTPException(400, "没有找到该项目")
    db.delete(indb)
    return True

@app.post("/add/")
async def add_goods(goods: GooodsType, db = Depends(get_db), _=Depends(oauth2_scheme)) -> bool:
    
    if db.query(
        exists().where( Goods.name == goods.name )
    ).scalar():
        raise HTTPException(400, "该项目已存在! 禁止重复添加")


    new = Goods(name = goods.name, mark = goods.mark, unit = goods.unit, quan = goods.quan)
    db.add(new)
    db.commit()
    return new

if __name__ == '__main__':
    if sys.argv.__len__() > 1:
        args = sys.argv
        if args[1] == 'create':
            # create database
            db_create()
            exit()
        elif args[1] == 'drop':
            db_drop()
            exit()
        elif args[1] == 'fake':
            db_fake()
            exit()

    run_uvicorn(app, host="0.0.0.0", port=8000)