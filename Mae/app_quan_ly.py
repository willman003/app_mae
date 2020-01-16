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
    dia_chi_frame = url_for('cap_nhat_tu_API')
    if request.form.get('Th_Ma_so'):
        man_hinh = request.form.get('Th_Ma_so')
        if man_hinh == "QL_Don_hang":
            dia_chi_frame = "/QL-don-hang"
        elif man_hinh == "QL_Kho":
            dia_chi_frame = url_for('ql_kho')
        elif man_hinh == "QL_Doanh_thu":
            dia_chi_frame = "/QL-doanh-thu"
        elif man_hinh == "Admin":
            dia_chi_frame = "/admin"    
        
    return render_template('Quan_ly/MH_Chinh.html', dia_chi_frame = dia_chi_frame)

@app.route('/cap-nhat-don-hang',methods=['GET','POST'])
def cap_nhat_tu_API():
    thong_bao = ''
    if request.method == 'POST':
        for item in Lay_danh_sach_order():
            order = Lay_thong_tin_chi_tiet_order(item['salesOrder']['orderNumber'])
            cap_nhat_hoa_don_database(order)
        thong_bao = "Cập nhật hoàn tất lúc %s" % datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    return render_template('Quan_ly/QL_don_hang/Cap_nhat_don_hang.html', thong_bao = thong_bao)

@app.route('/QL-don-hang', methods =['GET','POST'])
def ql_don_hang():
    if not current_user.is_authenticated or current_user.ma_loai_nguoi_dung != 1:
        return redirect(url_for('dang_nhap', next=request.url))
    dia_chi = ''
    if request.form.get('Th_hoa_don'):
        dieu_khien = request.form.get('Th_hoa_don')
        if dieu_khien == 'ChoLayHang':
            dia_chi = url_for('ql_don_hang_waiting')
        elif dieu_khien == 'DangVanChuyen':
            dia_chi = url_for('ql_don_hang_dang_van_chuyen')
        elif dieu_khien == 'Huy':
            dia_chi = url_for('ql_don_hang_huy')
        elif dieu_khien == 'TheoMaHD':
            dia_chi = url_for('ql_don_hang_theo_ma')
        
    return render_template('Quan_ly/MH_QL_don_hang.html', dia_chi = dia_chi)

@app.route("/QL-don-hang/cho-lay-hang", methods = ['GET','POST'])
def ql_don_hang_waiting():
    hoa_don = dbSession.query(Hoa_don).filter(Hoa_don.ma_van_don == None).all()
    
    return render_template('Quan_ly/QL_don_hang/QL_don_hang_all.html', hoa_don = hoa_don)

@app.route("/QL-don-hang/dang-van-chuyen", methods = ['GET','POST'])
def ql_don_hang_dang_van_chuyen():
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

@app.route("/QL-don-hang/huy", methods = ['GET','POST'])
def ql_don_hang_huy():
    danh_sach_order = Lay_danh_sach_order()
    ds_order_moi = []
    for item in danh_sach_order:
        order = item['salesOrder']
        if order['orderStatus'] == 13:
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

@app.route("/QL-don-hang/theo-ma-hd", methods = ['GET','POST'])
def ql_don_hang_theo_ma():
    form = Form_QL_don_hang()
    chi_tiet_order = None
    tieu_de = ''
    trang_thai ={2:"Mới",6:"Đang vận chuyển",13:"Huỷ"}
    if form.validate_on_submit():
        chi_tiet_order = Lay_thong_tin_chi_tiet_order(str(form.ma_hoa_don_tim_kiem.data))
        if chi_tiet_order.get('salesOrder'):
            tieu_de = 'Đơn hàng ' + chi_tiet_order['salesOrder']['orderNumber']
        else:
            chi_tiet_order = None
            tieu_de = 'Không tìm thấy mã hoá đơn!'
    return render_template('/Quan_ly/QL_don_hang/QL_don_hang_theo_ma_hd.html', trang_thai = trang_thai, tieu_de = tieu_de, form = form, chi_tiet_order = chi_tiet_order)

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

@app.route("/Ql-don-hang/in-hoa-don/hd_<int:hd_id>", methods =['GET','POST'])
def in_hoa_don(hd_id):
    order = Lay_thong_tin_chi_tiet_order(str(hd_id))
    
    chi_tiet_order = order['salesOrder']
    don_hang = order['salesOrderDetails']
    tong_tien = 0
    for item in don_hang:
        tong_tien += item['subTotal']
    tong_tien += chi_tiet_order['shippingFee']
    return render_template('Quan_ly/QL_don_hang/Hoa_don.html', chi_tiet_order = chi_tiet_order, don_hang = don_hang, tong_tien = tong_tien)

@app.route('/QL-kho', methods = ['GET','POST'])
def ql_kho():
    dia_chi = ''
    if request.method == 'POST':
        dieu_khien = request.form.get('Th_kho_hang')
        if dieu_khien == 'NhapHang':
            dia_chi = url_for('ql_kho_nhap_hang')
        elif dieu_khien == 'SoLuongTon':
            dia_chi = url_for('ql_so_luong_ton')

    return render_template('Quan_ly/QL_kho_hang/MH_QL_kho_hang.html', dia_chi = dia_chi)

@app.route('/QL-kho/nhap-hang', methods = ['GET','POST'])
def ql_kho_nhap_hang():
    form = Form_tim_kiem_nhap_hang()
    san_pham = []
    if form.validate_on_submit():
        tim_kiem = form.noi_dung.data
        
        if tim_kiem.isdigit():
            san_pham = dbSession.query(San_pham).filter(San_pham.ma_san_pham == int(tim_kiem)).all()
        else:
            chuoi_truy_van = '%'+tim_kiem.upper()+'%'
            san_pham = dbSession.query(San_pham).filter(San_pham.ten_san_pham.like(chuoi_truy_van)).all()
    
    return render_template('Quan_ly/QL_kho_hang/Nhap_hang.html', form = form, san_pham = san_pham)

@app.route('/QL-kho/nhap/sp_<int:ma_sp>', methods = ['GET','POST'])
def ql_kho_nhap_chi_tiet(ma_sp):
    if not current_user.is_authenticated or current_user.ma_loai_nguoi_dung != 1:
        return redirect(url_for('dang_nhap', next=request.url))
    form = Form_nhap_hang()
    san_pham = dbSession.query(San_pham).filter(San_pham.ma_san_pham == ma_sp).first()
    chuoi_thong_bao = ''
    if form.validate_on_submit():
        so_luong_nhap = form.so_luong_nhap.data
        san_pham.so_luong_ton += so_luong_nhap
        dbSession.add(san_pham)
        dbSession.commit()
        chuoi_thong_bao = "Đã thêm " + str(so_luong_nhap) + " "+ san_pham.ten_san_pham + " vào kho hàng"
    return render_template('Quan_ly/QL_kho_hang/Chi_tiet_nhap_hang.html', chuoi_thong_bao = chuoi_thong_bao, form = form, san_pham = san_pham)

@app.route('/QL-kho/ton-kho', methods = ['GET', 'POST'])
def ql_so_luong_ton():
    if not current_user.is_authenticated or current_user.ma_loai_nguoi_dung != 1:
        return redirect(url_for('dang_nhap', next=request.url))
    form = Form_tim_kiem()
    san_pham= []
    if form.validate_on_submit():
        tim_kiem = form.noi_dung.data
        if tim_kiem.isdigit():
            san_pham = dbSession.query(San_pham).filter(San_pham.ma_san_pham == tim_kiem).all()
        else:
            chuoi_truy_van = '%'+tim_kiem.upper()+'%'
            san_pham = dbSession.query(San_pham).filter(San_pham.ten_san_pham.like(chuoi_truy_van)).all()
    
    return render_template('Quan_ly/QL_kho_hang/Ton_kho.html', form=form, san_pham = san_pham)

init_login()
admin = Admin(app, name = "Admin", index_view=MyAdminIndexView(name="Admin"), template_mode='bootstrap3')
admin.add_view(admin_view(Loai_nguoi_dung, dbSession, 'Loại người dùng'))
admin.add_view(admin_view(Nguoi_dung, dbSession, 'Người dùng'))