# coding: utf-8
from flask import Flask, make_response
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
import os
from flask_sqlalchemy import SQLAlchemy
import settings
from db import get_data
from flask_babelex import Babel

base_path = os.path.abspath(os.path.dirname(__file__))

seven_db_settings = dict(
    host='rm-wz9iar6fx9ei3xa324o.mysql.rds.aliyuncs.com',
    port=3306,
    user='qiuxin',
    password='QiuXin2017',
    database='rrshop'
)


def get_db_uri():
    db_uri = 'mysql+pymysql://{user}:{password}@{host}' \
             '/{database}'.format(**seven_db_settings)
    return db_uri


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'
db = SQLAlchemy(app)
babel = Babel(app)


class IndexView(BaseView):
    @expose('/')
    def index(self):
        try:
            update_stock()
        except Exception as e:
            print('update stock error:', e)
        else:
            print('update stokck success')
        return make_response(u'<h1>更新成功，点击<a href="/admin/record/">查看库存</a></h1>')


admin = Admin(app, name=u'后台管理系统')
admin.add_view(IndexView(name=u'刷新库存'))


class Record(db.Model):
    __tablename__ = 'ims_ewei_export_record'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_code = db.Column(db.String(30))
    title = db.Column(db.String(100))
    color = db.Column(db.String(20))
    size = db.Column(db.String(20))
    shop0 = db.Column(db.Integer)
    shop1 = db.Column(db.Integer)
    shop2 = db.Column(db.Integer)
    shop3 = db.Column(db.Integer)
    shop4 = db.Column(db.Integer)
    shop5 = db.Column(db.Integer)
    shop6 = db.Column(db.Integer)
    shop7 = db.Column(db.Integer)
    shop8 = db.Column(db.Integer)
    shop9 = db.Column(db.Integer)


class RecordView(ModelView):
    can_create = False
    column_labels = dict(
        order_code=u'订单号',
        title=u'商品名称',
        color=u'颜色',
        size=u'尺码',
        shop0=u'建华店',
        shop1=u'大岗店',
        shop2=u'洛溪店',
        shop3=u'钟村店',
        shop4=u'市桥店',
        shop5=u'富怡店',
        shop6=u'南进店',
        shop7=u'石楼店',
        shop8=u'中华店',
        shop9=u'网店',
    )

    def __init__(self, session, **kwargs):
        super(RecordView, self).__init__(Record, session, **kwargs)


def save_data():
    for data in get_data(db, Record):
        record = Record(**dict(
            order_code=data[0],
            title=data[1],
            color=data[2],
            size=data[3],
            shop0=data[4],
            shop1=data[5],
            shop2=data[6],
            shop3=data[7],
            shop4=data[8],
            shop5=data[9],
            shop6=data[10],
            shop7=data[11],
            shop8=data[12],
            shop9=data[13],
        ))
        db.session.add(record)
    db.session.commit()    


def clear_data():
    db.session.query(Record).delete()
    db.session.commit()

def update_stock():
    save_data()


admin.add_view(RecordView(db.session, name=u'库存查询系统'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

