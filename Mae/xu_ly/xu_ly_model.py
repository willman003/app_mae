from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine



Base = declarative_base()


# from Mae import app, db



#------CLASS cho Web bán hàng------#
class Loai_san_pham(Base):
    __tablename__ = 'loai_san_pham'
    ma_loai = Column(Integer, nullable = False, primary_key = True)
    ten_loai = Column(String(50), nullable = False)
    mo_ta = Column(Text)
    
    def __str__(self):
        return self.ten_category

class San_pham(Base):
    __tablename__ = 'san_pham'
    ma_san_pham = Column(Integer, nullable = False, primary_key = True)
    ten_san_pham = Column(String(100), nullable = False)
    ma_loai = Column(Integer, ForeignKey('loai_san_pham.ma_loai'))
    gia_ban = Column(Integer, nullable = False)
    gia_nhap = Column(Integer, nullable = False, default = 0)
    so_luong_ton = Column(Integer, nullable = False, default = 0)
    id_sendo = Column(Integer)
    thuoc_tinh = Column(String(200))
    
    loai_san_pham = relationship(Loai_san_pham, backref='san_pham')
    def __str__(self):
        return self.ten_san_pham

    def get_id(self):
        return self.ma_san_pham

    
    
class Loai_nguoi_dung(Base):
    __tablename__ = 'loai_nguoi_dung'
    ma_loai_nguoi_dung = Column(Integer, nullable = False, primary_key = True)
    ten_loai_nguoi_dung = Column(String(100), nullable = False)
    def __str__(self):
        return self.ten_loai_nguoi_dung


class Nguoi_dung(Base):
    __tablename__ = 'nguoi_dung'
    ma_nguoi_dung = Column(Integer, nullable = False, primary_key = True)
    ma_loai_nguoi_dung = Column(Integer, ForeignKey('loai_nguoi_dung.ma_loai_nguoi_dung'))
    ho_ten = Column(String(200))
    ten_dang_nhap = Column(String(64), nullable = False)
    mat_khau_hash = Column(String(128), nullable = False)
    
    loai_nguoi_dung = relationship(Loai_nguoi_dung,backref='nguoi_dung') 
    @property
    def is_authenticated(self):
        return True
    @property
    def is_active(self):
        return True
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.ma_nguoi_dung

    def __unicode__(self):
        return self.ho_ten
    
    def __str__(self):
        return self.ten_dang_nhap
   

class Khach_hang(Base):
    __tablename__ = 'khach_hang'
    ma_khach_hang = Column(Integer, nullable = False, primary_key = True)
    ten_khach_hang = Column(String(100), nullable = False)
    email=Column(String(100))
    dia_chi = Column(String(200), nullable = False)
    dien_thoai = Column(String(20), nullable = False)
    
    def __str__(self):
        return self.dia_chi

    def get_id(self):
        return self.ma_khach_hang
    
class Hoa_don(Base):
    __tablename__ = 'hoa_don'
    ma_hoa_don = Column(Integer, nullable = False, primary_key = True)
    ngay_tao_hoa_don = Column(DateTime, nullable = False)
    ma_khach_hang = Column(Integer, ForeignKey('khach_hang.ma_khach_hang'))
    tong_tien = Column(Float, nullable = False)
    ma_hoa_don_sendo = Column(String(50))
    nha_van_chuyen = Column(String(255))
    ma_van_don = Column(String(100))
    trang_thai = Column(Integer)
    ghi_chu = Column(Text)
    da_in_hd = Column(Integer, default = 0)
    da_cap_nhat_kho = Column(Integer, default = 0)
    
    khach_hang = relationship(Khach_hang, backref = 'hoa_don')
    def __repr__(self):
        return "<Ma_hoa_don = %d>" % self.ma_hoa_don

    def get_id(self):
        return self.ma_hoa_don

class Don_hang(Base):
    __tablename__ = 'don_hang'
    id = Column(Integer, nullable =False, primary_key = True)
    ma_hoa_don = Column(Integer, ForeignKey('hoa_don.ma_hoa_don'))
    ma_san_pham = Column(Integer)
    ten_san_pham = Column(String(100), nullable = False)
    so_luong = Column(Integer, nullable = False)
    don_gia = Column(Integer)
    ghi_chu = Column(Text)
    hoa_don = relationship(Hoa_don, backref = 'don_hang', foreign_keys=[ma_hoa_don])
    
    def __repr__(self):
        return "<Ma_hoa_don = %d>" % self.ma_hoa_don


engine = create_engine('sqlite:///Mae/du_lieu/ql_mae.db?check_same_thread=False')
Base.metadata.create_all(engine)



