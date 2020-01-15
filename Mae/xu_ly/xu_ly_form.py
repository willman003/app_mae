from Mae import app

from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, IntegerField, StringField, PasswordField, SelectField, DateTimeField
from wtforms import form, fields, validators
from wtforms.widgets.html5 import NumberInput

import flask_login as login
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import sessionmaker

from flask_ckeditor import CKEditorField

from Mae.xu_ly.xu_ly_model import *
from Mae.xu_ly.xu_ly_form import *

Base.metadata.bind = engine
DBsession = sessionmaker(bind = engine)
dbSession = DBsession()

class Form_mua_hang(FlaskForm):
    so_luong = IntegerField('Nhập số lượng', widget=NumberInput())
    submit_1 = SubmitField('Thêm vào giỏ hàng')

class Form_dang_nhap(FlaskForm):
    ten_dang_nhap = fields.StringField('Tên đăng nhập', [validators.required()])
    password = fields.PasswordField('Mật khẩu', [validators.required()])

    def validate_ten_dang_nhap(self, ten_dang_nhap):
        user = self.get_user()
        if user is None:
            raise validators.ValidationError('Tên đăng nhập không tồn tại!')
        if not check_password_hash(user.mat_khau_hash, self.password.data):
            raise validators.ValidationError('Mật khẩu không hợp lệ!')
    
    def get_user(self):
        return dbSession.query(Nguoi_dung).filter_by(ten_dang_nhap = self.ten_dang_nhap.data).first()

class Form_dang_ky(FlaskForm):
    ho_ten = fields.StringField('Họ tên:', [validators.required()])
    email = fields.StringField('Email:', [validators.required()])
    ten_dang_nhap = fields.StringField('Tên đăng nhập:', [validators.required()])
    mat_khau = fields.PasswordField('Mật khẩu:',[validators.required()])
    
    
    def validate_ten_dang_nhap(self, ten_dang_nhap):
        if dbSession.query(Nguoi_dung).filter_by(ten_dang_nhap = self.ten_dang_nhap.data).count() > 0:
            raise validators.ValidationError('Tên đăng nhập đã được sử dụng!')
    
     

class Form_hoa_don(FlaskForm):
    ho_ten = fields.StringField('Họ tên:', [validators.required()])
    dia_chi = fields.StringField('Địa chỉ:', [validators.required()])
    dien_thoai = fields.StringField('Số điện thoại:', [validators.required()])
    ghi_chu = fields.TextAreaField('Ghi chú:')
    
    def tao_hoa_don(self, ma_khach_hang, tong_tien):
        hoa_don = Hoa_don()
        hoa_don.ma_khach_hang = ma_khach_hang
        hoa_don.tong_tien = tong_tien
        hoa_don.ngay_tao_hoa_don = datetime.now()
        hoa_don.dia_chi_giao_hang = self.dia_chi.data
        hoa_don.so_dien_thoai_nguoi_nhan = self.dien_thoai.data
        note = ''
        if self.ghi_chu.data != None:
            note = "[KHÁCH], " + self.ghi_chu.data
        hoa_don.ghi_chu = note
        hoa_don.trang_thai = 0
        dbSession.add(hoa_don)
        dbSession.commit()
        return hoa_don.get_id()

class Form_QL_don_hang(FlaskForm):
    ma_hoa_don_tim_kiem = fields.IntegerField([validators.required()])
    ngay_tim_kiem = fields.DateField(format='%Y-%m-%d')

class Form_tim_kiem(FlaskForm):
    noi_dung = fields.StringField()

class Form_tim_kiem_nhap_hang(FlaskForm):
    noi_dung = fields.StringField()
    submit = fields.SubmitField('Tìm kiếm')

class Form_nhap_hang(FlaskForm):
    so_luong_nhap = fields.IntegerField(widget=NumberInput())
    

class Form_y_kien(FlaskForm):
    ma_khach_hang = fields.IntegerField('Mã khách hàng')
    tieu_de = fields.StringField('Tiêu đề')
    diem_danh_gia = fields.IntegerField('Điểm đánh giá', widget=NumberInput())
    noi_dung = CKEditorField()
    submit_2 = SubmitField('Gửi ý kiến')

class Form_huy_don_hang(FlaskForm):
    li_do = fields.TextAreaField()
    submit = fields.SubmitField('Đồng ý')

class Form_lua_chon(FlaskForm):
    lua_chon = fields.SelectField('Trạng thái:',choices=[('0','Chưa thanh toán'),('1','Đã thanh toán'),('2','Huỷ')])
    submit = SubmitField('Xem')

def init_login():
	login_manager = login.LoginManager()
	login_manager.init_app(app)

	# Create user loader function
	@login_manager.user_loader
	def load_user(user_id):
		return dbSession.query(Nguoi_dung).get(user_id)




    