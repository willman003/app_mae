from Mae import app

from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, session, flash, Markup

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
import flask_admin as admin

from flask_login import current_user, login_user
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.orm import sessionmaker, configure_mappers
from sqlalchemy import exc,asc,desc, and_, or_
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
        if dieu_khien == 'ChuaInHD':
            dia_chi = url_for('ql_don_hang_chua_in')
        elif dieu_khien == 'DaInHD':
            dia_chi = url_for('ql_don_hang_da_in')
        elif dieu_khien == 'Huy':
            dia_chi = url_for('ql_don_hang_huy')
        elif dieu_khien == 'TheoMaHD':
            dia_chi = url_for('ql_don_hang_theo_ma')
        
    return render_template('Quan_ly/MH_QL_don_hang.html', dia_chi = dia_chi)

@app.route("/QL-don-hang/chua-in", methods = ['GET','POST'])
def ql_don_hang_chua_in():
    hoa_don = dbSession.query(Hoa_don).join(Khach_hang).filter(and_(Hoa_don.da_in_hd == 0, or_(Hoa_don.trang_thai == 2,Hoa_don.trang_thai == 3,Hoa_don.trang_thai == 6) )).all()
    
    
    return render_template('Quan_ly/QL_don_hang/QL_don_hang_all.html', hoa_don = hoa_don)

@app.route("/QL-don-hang/da-in", methods = ['GET','POST'])
def ql_don_hang_da_in():
    hoa_don = dbSession.query(Hoa_don).join(Khach_hang).filter(and_(Hoa_don.da_in_hd == 1,or_(Hoa_don.trang_thai == 2,Hoa_don.trang_thai == 3,Hoa_don.trang_thai == 6))).all()
    return render_template('Quan_ly/QL_don_hang/QL_don_hang_all.html', hoa_don = hoa_don)

@app.route("/QL-don-hang/huy", methods = ['GET','POST'])
def ql_don_hang_huy():
    hoa_don = dbSession.query(Hoa_don).join(Khach_hang).filter(Hoa_don.trang_thai == 13).all()
    return render_template('/Quan_ly/QL_don_hang/QL_don_hang_all.html', hoa_don = hoa_don)

@app.route("/QL-don-hang/theo-ma-hd", methods = ['GET','POST'])
def ql_don_hang_theo_ma():
    form = Form_QL_don_hang()
    hoa_don = None
    tieu_de = ''
    trang_thai ={2:"Mới",6:"Đang vận chuyển",13:"Huỷ"}
    if form.validate_on_submit():
        hoa_don = dbSession.query(Hoa_don).join(Khach_hang).filter(Hoa_don.ma_hoa_don_sendo == str(form.ma_hoa_don_tim_kiem.data)).first()
        if hoa_don == None:
            tieu_de = 'Không tìm thấy mã hoá đơn ' + str(form.ma_hoa_don_tim_kiem.data)
        else:
            tieu_de = 'Đơn hàng ' + hoa_don.ma_hoa_don_sendo

            
    return render_template('Quan_ly/QL_don_hang/QL_don_hang_theo_ma_hd.html', trang_thai = trang_thai, tieu_de = tieu_de, form = form, hoa_don = hoa_don)


@app.route('/QL-don-hang/hd_<string:hd_id>', methods =['GET','POST'])
def chi_tiet_order(hd_id):
    order = Lay_thong_tin_chi_tiet_order(hd_id)
    
    chi_tiet_order = order['salesOrder']
    don_hang = order['salesOrderDetails']
    tong_tien = 0
    for item in don_hang:
        tong_tien += item['subTotal']
    tong_tien += chi_tiet_order['shippingFee']
    hoa_don = dbSession.query(Hoa_don).filter(Hoa_don.ma_hoa_don_sendo == hd_id).first()
    trang_thai_1 = {0:"Chưa in hoá đơn",1:"Đã in hoá đơn"}
    trang_thai_2 = {0:"Chưa cập nhật kho",1:"Đã cập nhật kho"}
    return render_template("Quan_ly/QL_don_hang/QL_don_hang_chi_tiet.html", trang_thai_2 = trang_thai_2, trang_thai_1 = trang_thai_1, hoa_don = hoa_don, tong_tien = tong_tien, chi_tiet_order = chi_tiet_order, don_hang = don_hang)

@app.route("/Ql-don-hang/in-hoa-don/hd_<string:hd_id>", methods =['GET','POST'])
def in_hoa_don(hd_id):
    order = Lay_thong_tin_chi_tiet_order(hd_id)
    
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

@app.route('/QL-kho/cap-nhat-kho-hang/hd_<string:hd_id>', methods =['GET','POST'])
def ql_kho_xuat_hang(hd_id):
    order = Lay_thong_tin_chi_tiet_order(hd_id)
    don_hang = order['salesOrderDetails']
    hd = dbSession.query(Hoa_don).filter(Hoa_don.ma_hoa_don_sendo == hd_id).first()
    for item in don_hang:
        sp = dbSession.query(San_pham).filter(San_pham.id_sendo == item['productVariantId']).first()
        sp.so_luong_ton -= item['quantity']
        
        dbSession.add(sp)
        dbSession.commit()
    hd.da_cap_nhat_kho = 1
    dbSession.add(hd)
    dbSession.commit()
    return redirect(url_for('chi_tiet_order', hd_id = hd_id))

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