from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse
from CONFIG import CONFIG
from db import create_all as db_create, drop_all as db_drop, create_fake as db_fake, Goods, Category, database

from typing import Optional, List, Union, Generator
from jose import jwt
from pydantic import BaseModel

from uvicorn import run as run_uvicorn
import sys

app = FastAPI()


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=CONFIG.IVM_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

def get_db():
    with database.atomic() as txn:
        try:
            yield txn
        finally:
            txn.rollback()

class CategoryType_(BaseModel):
    key: str
    name: str
    unit: Optional[Union[str, None]]
    mark: Optional[str]

    class Config:
        orm_mode = True

class GoodsType(BaseModel):
    key: str
    name: str
    quan: float
    flag: Optional[str] = ""
    # belongs: CategoryType_

    class Config:
        orm_mode = True

class CategoryType(CategoryType_):
    goods: List[GoodsType] = []


oauth2 = OAuth2PasswordBearer(tokenUrl='/login')


def oauth2_scheme(token=Depends(oauth2)):
    data = jwt.decode(token, key=CONFIG.IVM_SECRET_KEY, algorithms=CONFIG.IVM_ALGORITHM)
    if data.get('user_name') == CONFIG.IVM_USERNAME and data.get('password') == CONFIG.IVM_PASSWORD:
        return True
    else:
        raise HTTPException(401, "用户校验错误! 请重新登录再试!")


@app.post('/login')
async def login(data: OAuth2PasswordRequestForm = Depends()):
    if (data.username == CONFIG.IVM_USERNAME) and (data.password == CONFIG.IVM_PASSWORD):
        return {
            "access_token": jwt.encode(claims={"user_name": data.username, 'password': data.password},
                                       key=CONFIG.IVM_SECRET_KEY, algorithm=CONFIG.IVM_ALGORITHM),
            "token_type": "bearer"
        }
    else:
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post('/list')
async def list_goods(db=Depends(get_db), _=Depends(oauth2_scheme)) -> List[CategoryType]:
    ls = []
    for cate in Category.select():
        ls_ = []
        for goods in cate.goods:
            item = GoodsType.from_orm((goods))
            item.flag = ""
            ls_.append(item)

        ls.append(CategoryType(key=cate.key, name=cate.name, unit=cate.unit, mark=cate.mark, goods=ls_))

    return ls

@app.post('/update')
async def update_goods(
    cate: CategoryType = Body(...),
    __=Depends(get_db), _=Depends(oauth2_scheme)
) -> GoodsType:
    # try:
    if cate.key == "add":
        # 新建分类
        indb: Category = Category.create(name=cate.name, unit=cate.unit, mark=cate.mark)
    else:
        indb: Category = Category.get_by_id(cate.key)
        indb.name = cate.name
        indb.mark = cate.mark
        indb.unit = cate.unit
        indb.save()

    goods_ls = []
    for goods in cate.goods:
        # indb_ = Goods.get_or_none(Goods.key == )
        if goods.flag:
            if goods.flag == 'add':
                # 新建
                new = Goods.create(name = goods.name, quan = goods.quan, belongs = indb)
                goods_ls.append(GoodsType(key=str(new.key), name=new.name, quan=new.quan, flag=""))
            elif goods.flag == 'del':
                # 删除
                Goods.delete().where(Goods.key == goods.key).execute()
        else:
            # 修改
            inst: Goods = Goods.get_by_id(goods.key)
            inst.update(name = goods.name, quan = goods.quan)
            inst.save()
            goods_ls.append(goods)
            
    return CategoryType(key = cate.key, name = indb.name, mark = indb.mark, unit = indb.unit, goods=goods_ls)

    # except:
    #     raise HTTPException(400, "没有找到该项目")


# ===== 已经合并到 update 中 =====
# @app.post('/add_category')
# async def add_category(
#     # key: str = Body(),
#     name: str = Body(...), 
#     unit: str = Body(...), 
#     mark: str = Body(...),
#     db=Depends(get_db),
#     _=Depends(oauth2_scheme)) -> CategoryType:
#     return Category.create(name=name, unit=unit, mark=mark)

@app.post('/del')
async def del_category(cate: CategoryType = Body(...), db=Depends(get_db), _=Depends(oauth2_scheme)) -> bool:
    return Category.delete().where(Category.key == cate.key).execute()


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

    run_uvicorn(app, host="localhost", port=8000)