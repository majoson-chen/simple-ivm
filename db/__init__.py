from sqlalchemy import create_engine, Column, String, Integer, Float, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from CONFIG import CONFIG

Base = declarative_base()
engine = create_engine(CONFIG.DB_URI, connect_args={"check_same_thread": False})
DBSession = sessionmaker(bind=engine)

def create():
    Base.metadata.create_all(engine)

def fake():
    fakeGoods= [
        {
            "key": 0,
            "name": "苹果",
            "quan":  100,
            "unit": "千克"
        },{
            "key": 1,
            "name": "凤梨",
            "quan":  200,
            "unit": "个"
        },{
            "key": 2,
            "name": "香蕉",
            "quan":  300,
            "unit": "箱"
        },{
            "key": 3,
            "name": "西瓜",
            "quan":  125,
            "unit": "个",
            "mark": "快过期了"
        },
        {
            "key": 4,
            "name": "水蜜桃",
            "quan":  60,
            "unit": "千克",
            "mark": "快点卖掉"
        },
        {
            "key": 5,
            "name": "哈密瓜",
            "quan":  88,
            "unit": "个",
            "mark": "不能久放"
        },
    ]
    with DBSession() as sn:
        for good in fakeGoods:
            sn.add(Goods(**good))
        sn.commit()
        

def drop():
    Base.metadata.drop_all(engine)


class Goods(Base):
    __tablename__ = "ivm_goods"

    key   = Column(Integer, primary_key=True)
    name  = Column(String(64), unique=True) 
    quan  = Column(Float(decimal_return_scale=3))
    unit  = Column(String(16))
    mark  = Column(Text())