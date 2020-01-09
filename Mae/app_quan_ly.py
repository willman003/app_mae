from Mae import app

from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, session, flash

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
import flask_admin as admin

from flask_login import current_user, login_user
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.orm import sessionmaker, configure_mappers
from sqlalchemy import exc,asc,desc
from flask_sqlalchemy import Pagination

from flask_sqlalchemy import BaseQuery

from Mae.xu_ly.xu_ly_model import *
from Mae.xu_ly.xu_ly_form import *
from Mae.xu_ly.xu_ly import *

configure_mappers()
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
dbSession = DBSession()

class MyAdminIndexView(admin.AdminIndexView):
    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('dang_nhap'))
        return super(MyAdminIndexView, self).render('admin/index.html')

class admin_view(ModelView):
    column_display_pk = True
    can_create = True
    can_delete = True
    can_export = False

@app.route('/', methods=['GET','POST'])
def index():
    if not current_user.is_authenticated or current_user.ma_loai_nguoi_dung != 1:
        return redirect(url_for('log_in', next=request.url))
    dia_chi_frame = ''
    if request.form.get('Th_Ma_so'):
        man_hinh = request.form.get('Th_Ma_so')
        if man_hinh == "QL_Don_hang":
            dia_chi_frame = "/QL-don-hang"
        elif man_hinh == "QL_Kho":
            dia_chi_frame = "/QL-kho"
        elif man_hinh == "QL_Doanh_thu":
            dia_chi_frame = "/Ql-doanh-thu"
        elif man_hinh == "Admin":
            dia_chi_frame = "/admin"    
        
    return render_template('Quan_ly/MH_Chinh.html', dia_chi_frame = dia_chi_frame)

@app.route('/QL-don-hang', methods =['GET','POST'])
def ql_don_hang():
    if not current_user.is_authenticated or current_user.ma_loai_nguoi_dung != 1:
        return redirect(url_for('dang_nhap', next=request.url))
    dia_chi = ''
    if request.form.get('Th_hoa_don'):
        dieu_khien = request.form.get('Th_hoa_don')
        if dieu_khien == 'All':
            dia_chi = '/QL-don-hang/moi'
        elif dieu_khien == 'TimKiem':
            dia_chi = '/QL-don-hang/ma-hoa-don'
        elif dieu_khien == 'TheoNgay':
            dia_chi ='/QL-don-hang/theo-ngay/1'
        elif dieu_khien == 'TheoTrangThai':
            dia_chi = '/QL-don-hang/theo-trang-thai/page_1'
        
    return render_template('Quan_ly/MH_QL_don_hang.html', dia_chi = dia_chi)

@app.route("/QL-don-hang/moi", methods = ['GET','POST'])
def ql_don_hang_moi():
    danh_sach_order = Lay_danh_sach_order()
    ds_order_moi = []
    for item in danh_sach_order:
        order = item['salesOrder']
        if order['orderStatus'] == 6:
            ds_order_moi.append(item)
    ds_chi_tiet_order = []
    for item in ds_order_moi:
        order = item['salesOrder']
        chi_tiet_order = Lay_thong_tin_chi_tiet_order(order['orderNumber'])
        dict_temp = {}
        dict_temp['salesOrder'] = order
        dict_temp['salesOrder_info_detail'] = chi_tiet_order['salesOrder']
        dict_temp['salesOrderDetails'] = chi_tiet_order['salesOrderDetails']
        ds_chi_tiet_order.append(dict_temp)
    return render_template('/Quan_ly/QL_don_hang/QL_don_hang_all.html', ds_chi_tiet_order = ds_chi_tiet_order)

@app.route('/QL-don-hang/hd_<int:hd_id>', methods =['GET','POST'])
def chi_tiet_order(hd_id):
    order = Lay_thong_tin_chi_tiet_order(str(hd_id))
    chi_tiet_order = order['salesOrder']
    don_hang = order['salesOrderDetails']
    tong_tien = 0
    for item in don_hang:
        tong_tien += item['subTotal']
    tong_tien += chi_tiet_order['shippingFee']

    return render_template("Quan_ly/QL_don_hang/QL_don_hang_chi_tiet.html", tong_tien = tong_tien, chi_tiet_order = chi_tiet_order, don_hang = don_hang)

init_login()
admin = Admin(app, name = "Admin", index_view=MyAdminIndexView(name="Admin"), template_mode='bootstrap3')
admin.add_view(admin_view(Loai_nguoi_dung, dbSession, 'Loại người dùng'))
admin.add_view(admin_view(Nguoi_dung, dbSession, 'Người dùng'))