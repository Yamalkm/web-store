from sqlalchemy import Column, Integer, String, Boolean, DateTime
from flask_login import UserMixin
from datetime import datetime

import db


class Producto(db.Base):
    __tablename__ = 'producto'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    contenido = Column(String(200), nullable=False)
    categoria = Column(String(200), nullable=False)
    precio = Column(String(200), nullable=False)
    stock= Column(Integer)
    contador = Column(Integer)
    hecha = Column(Boolean)
    total=Column(Integer)

    def __init__(self, contenido, categoria, precio,stock,contador,total, hecha):
        self.contenido = contenido
        self.categoria = categoria
        self.precio = precio
        self.stock = stock
        self.contador = contador
        self.total = total
        self.hecha = hecha
        print('Tarea creada con éxito')

class Vendido(db.Base):
    __tablename__ = 'vendido'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    contenido = Column(String(200), nullable=False)
    categoria = Column(String(200), nullable=False)
    precio = Column(String(200), nullable=False)
    stock = Column(Integer)
    contador = Column(Integer)
    id_compra = Column(Integer)
    id_cliente = Column(Integer)
    hecha = Column(Boolean)
    fecha=Column(DateTime, default=datetime.now)
    total = Column(Integer)

    def __init__(self, contenido, categoria, precio,stock,contador,id_compra,id_cliente,total, hecha):
        self.contenido = contenido
        self.categoria = categoria
        self.precio = precio
        self.stock = stock
        self.contador = contador
        self.id_compra = id_compra
        self.id_cliente = id_cliente
        self.total = total
        self.hecha = hecha
        print('Tarea creada con éxito')

    def __str__(self):
        return 'Tarea {}: {} :{} :{} ({})'.format(self.id, self.contenido, self.categoria, self.precio, self.hecha)


class Registros(UserMixin, db.Base):
    __tablename__ = 'registro'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    username = Column(String(200), nullable=False)
    mail = Column(String(200), nullable=False)
    password = Column(String(200), nullable=False)
    hecha = Column(Boolean, default=False)

    def __init__(self, username, mail, password, hecha):
        self.username = username
        self.mail = mail
        self.password = password
        self.hecha = hecha
        print('clientes creada con exito')

class Carrito(db.Base):
    __tablename__ = 'carrito'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    contenido = Column(String(200), nullable=False)
    categoria = Column(String(200), nullable=False)
    precio = Column(String(200), nullable=False)
    id_compra= Column(Integer)
    id_cliente = Column(Integer)
    stock=Column(Integer)
    hecha = Column(Boolean)

    def __init__(self, contenido, categoria, precio, hecha,id_compra, id_cliente,stock):
        self.contenido = contenido
        self.categoria = categoria
        self.precio = precio
        self.hecha = hecha
        self.id_compra = id_compra
        self.id_cliente = id_cliente
        self.stock = stock
        print('Tarea creada con éxito')

