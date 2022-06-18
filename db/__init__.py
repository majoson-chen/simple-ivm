from peewee import SqliteDatabase, Model, TextField, IntegerField, FloatField, UUIDField, DeferredForeignKey, Field
from uuid import uuid1, UUID
from random import randint
from typing import List
from CONFIG import CONFIG
MODELS = []

database = SqliteDatabase('data.db', pragmas={'foreign_keys': 1})

def create_all():
    database.create_tables(MODELS)

def drop_all():
    database.drop_tables(MODELS)

def create_fake():
    fakeGoods= [
        {
            # "key": uuid1(),
            "name": "苹果",
            "quan":  100,
        },{
            # "key": uuid1(),
            "name": "凤梨",
            "quan":  200,
        },{
            # "key": uuid1(),
            "name": "香蕉",
            "quan":  300,
        },{
            # "key": uuid1(),
            "name": "西瓜",
            "quan":  125,
        },
        {
            # "key": uuid1(),
            "name": "水蜜桃",
            "quan":  60,
        },
        {
            # "key": uuid1(),
            "name": "哈密瓜",
            "quan":  88,
        },
    ]

    with database.atomic():
        ca1 = Category.create(name = "A10", unit = "kg", mark="A10备注")
        ca2 = Category.create(name = "B10", unit = "件", mark="B10备注")
        for goods in fakeGoods:
            Goods.create(**goods, belongs=ca1 if randint(0,1) else ca2)

class BaseModel(Model):
    class Meta:
        database = database

# class UUIDField_(UUIDField):


#     def python_value(self, value):
#         return str(UUID(value)) # convert hex string to UUID

def register_model(cls):
    global MODELS
    MODELS.append(cls)
    return cls

@register_model
class Goods(BaseModel):
    key = TextField(primary_key=True, default=uuid1)
    name = TextField()
    quan = FloatField()
    # mark = TextField(default="")
    belongs = DeferredForeignKey ("Category", backref='goods', null=False)

    class Meta:
        table_name = "ivm_goods"

@register_model
class Category(BaseModel):
    key = TextField(primary_key=True, default=uuid1)
    name = TextField(unique=True, null=False)
    unit = TextField()
    mark = TextField(default="")
    goods: List[Goods]

    class Meta:
        table_name = "ivm_categories"