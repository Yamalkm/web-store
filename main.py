from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, login_user, login_required, logout_user,current_user
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
import plotly.express as px
import pandas as pd

from models import Producto, Registros, Carrito, Vendido
import db


app = Flask(__name__)
app.config['SECRET_KEY'] = 'password'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/producto.db'


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    sales = db.session.query(Vendido).all()
    data = {'Product': [sale.contenido for sale in sales],
            'Utilities': [sale.total for sale in sales]}

    df = pd.DataFrame(data)
    print(df.head())
    fig = px.bar(df, x='Product', y='Utilities', title='Sales by product')
    graph_html = fig.to_html(full_html=False)
    return render_template('admin.html', graph_html=graph_html)


@app.route('/productos', methods=['GET', 'POST'])
def productos():
    todos_los_productos = db.session.query(Producto).all()
    return render_template('productos.html', lista_de_productos=todos_los_productos)


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = db.session.query(Registros).filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.hecha:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('home'))
        else:
            error = 'Incorrect password or username'
            return render_template('login.html', error=error)

    return render_template('login.html', error=error)


@app.route("/")
def home():
    son = request.args.get('son', 0)
    todos_los_productos = db.session.query(Producto).all()
    return render_template("home.html", lista_de_productos=todos_los_productos,son=int(son))

@app.route("/profile")
def profile():
    user_id = current_user.id
    lista_usuarios = db.session.query(Registros).all()
    u=[]
    for i in lista_usuarios:
        if i.id ==user_id:
            u=i
    return render_template("profile.html", usuario=u)

@app.route("/venta")
def venta():
    user_id = current_user.id
    lista_carrito = db.session.query(Carrito).all()
    lista_productos=db.session.query(Producto).all()
    for d in lista_carrito:
        for s in lista_productos:
            if s.stock == 0 and d.id_cliente == user_id and s.id == d.id_compra:
                return redirect(url_for('carrito', mensaje=int(1)))
    for i in lista_carrito:
        for r in lista_productos:
            if i.id_cliente==user_id and i.id_compra == r.id and r.stock>0:
                vendido = Vendido(contenido=r.contenido, categoria=r.categoria, precio=r.precio,
                              id_compra=r.id, id_cliente=user_id, hecha=False, stock=r.stock,
                              total=r.total, contador=r.contador)
                db.session.add(vendido)
        db.session.commit()
    for p in lista_carrito:
        for s in lista_productos:
            if p.id_cliente == user_id and p.id_compra ==s.id and s.stock>0:
                s.stock -= 1
        db.session.commit()
    l=[]
    for e in lista_productos:
        if e.contador > 0:
            l.append(e)
    for j in lista_carrito:
        if j.id_cliente==user_id :
            db.session.delete(j)
            db.session.commit()
        db.session.commit()
    return render_template("venta.html",productos=l)




@app.route('/eliminar-carrito/<id>')
def quitar(id):
    t=int(id)
    user_id = current_user.id
    lista_carrito = db.session.query(Carrito).all()
    for i in lista_carrito:
        if i.id_compra == t and i.id_cliente == user_id:
            db.session.delete(i)
            db.session.commit()
    return redirect(url_for('carrito'))


@app.route('/comprando/<id>',methods=['GET', "POST"])
def comprando(id):
    producto = db.session.query(Producto).filter_by(id=int(id))
    return render_template('compras.html', productos=producto)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return render_template('login.html')

@app.route('/comprado/<id>', methods=['GET', "POST"])
@login_required
def comprado(id):
    user_id = current_user.id
    id=int(id)
    producto = db.session.query(Producto).get(int(id))
    print(producto.stock)
    if producto.stock > 0:
        vendido = Vendido(contenido=producto.contenido, categoria=producto.categoria, precio=producto.precio,
                          id_compra=producto.id, id_cliente=user_id, hecha=False, stock=producto.stock,
                          total=producto.total, contador=producto.contador)
        producto.stock -= 1
        db.session.add(vendido)
        db.session.commit()
        return redirect(url_for('confirmacion',id=id))
    elif producto.stock <= 0:
        producto = db.session.query(Producto).filter_by(id=int(id))
        comprado=1
        return render_template('compras.html', productos=producto,comprado=comprado)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Registros).get(int(user_id))

@app.route('/confirmacion')
def confirmacion():
    id = request.args.get('id', 0)
    producto = db.session.query(Producto).filter_by(id=int(id))
    print(producto)
    return render_template("vendido.html",productos=producto)

@app.route("/p", methods=["POST"])
def homes():
    return redirect(url_for('home'))

@app.route("/carrito")
def carrito():
    user_id = current_user.id
    lista_carrito = db.session.query(Carrito).all()
    lista_productos=db.session.query(Producto).all()
    u=[]
    t=0
    mensaje = request.args.get('mensaje', 0)
    stock=0
    total_precio = db.session.query(func.sum(Carrito.precio)).filter(Carrito.id_cliente == user_id).scalar()
    f='Start a shopping cart!'
    for d in lista_productos:
        for a in lista_carrito:
            if d.stock <= 0 and a.id_cliente == user_id:
                stock = 1
    for j in lista_productos:
        db.session.query(Producto).filter(Producto.id == j.id).update({Producto.contador: 0})
        producto = db.session.query(Producto).filter(Producto.id == j.id).first()
        for r in lista_carrito:
            if j.id==r.id_compra and r.id_cliente==user_id and j.stock>j.contador:
                producto.contador+=1
                t+=1
        db.session.commit()
    l=[]
    for s in lista_productos:
        db.session.query(Producto).filter(Producto.total == s.total).update({Producto.total: 0})
        total = db.session.query(Producto).filter(Producto.precio == s.precio).first()
        total.total= int(s.contador)*int(s.precio)
        db.session.commit()
    for c in lista_carrito:
        if c.id_compra and c.id_cliente==user_id:
            o=c.id_compra
            if o not in l:
                l.append(o)
    return render_template("carrito.html",producto=l, contador=u,compra_lista= lista_productos,
                           carrito_lista=lista_carrito, stock=stock, cliente=user_id, precio_total=total_precio,
                           articulos=t,texto=f, mensaje=int(mensaje))

@app.route('/actualizar-contador/<id>', methods=['POST'])
def actualizar_contador(id):
    product = db.session.query(Producto).get(int(id))
    user_id = current_user.id
    if product:
        change = int(request.form['change'])
        product.contador += change
        if product.contador >0 and product.stock>=product.contador:
            if change==1:
                carrito = Carrito(contenido=product.contenido, categoria=product.categoria, precio=product.precio,
                              id_compra=product.id, id_cliente=user_id, hecha=False, stock=product.stock)
                db.session.add(carrito)
            elif change==-1:
                y=int(id)
                producto = db.session.query(Carrito).all()
                for i in producto:
                    if i.id_compra == y:
                        db.session.delete(i)
                        db.session.commit()
                        break
        elif product.contador ==0:
            product.contador = 0
        db.session.commit()
    db.session.close()
    return redirect(url_for('carrito'))


@app.route("/compras/<id>", methods=['GET', "POST"])
@login_required
def compras(id):
    user_id = current_user.id
    producto = db.session.query(Producto).get(int(id))
    if producto.contador<=0:
        if producto.stock>0:
            carrito= Carrito(contenido=producto.contenido, categoria=producto.categoria,precio=producto.precio,
                     id_compra=producto.id, id_cliente=user_id, hecha=False, stock=producto.stock)
            db.session.add(carrito)
            db.session.commit()
            return redirect(url_for('carrito'))
        elif producto.stock<=0:
            stock=1
            return redirect(url_for('home', son=stock))
    else:
        return redirect(url_for('carrito'))


@app.route("/product", methods=['GET'])
def create():
    return render_template('create_product.html')


@app.route("/registrarse", methods=['GET', "POST"])
def registro():
    return render_template('registrarse.html')


@app.route("/registrar", methods=['GET', "POST"])
def registrar():
    comprobar = request.form['comprobar_registro']
    password = request.form['password_registro']
    hecha = True if request.form.get('hecha') else False
    hashed_password = generate_password_hash(password)
    registrar = Registros(username=request.form['username_registro'], mail=request.form['mail_registro'],
                          password=hashed_password, hecha=hecha)
    usuario = db.session.query(Registros).filter_by(username=registrar.username).first()
    if usuario ==None:
        usuario=Registros(username=None, mail=None,
                          password=None, hecha=None)
    if password == comprobar:
        if usuario.username != registrar.username:
            db.session.add(registrar)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return render_template('registrarse.html', mensaje='User already exists')
    else:
        return render_template('registrarse.html', mensaje='Incorrect password')


@app.route("/usuarios", methods=['GET', "POST"])
def usuario():
    todos_los_usuarios = db.session.query(Registros).all()
    return render_template("usuarios.html", lista_de_usuarios=todos_los_usuarios)


@app.route("/producto", methods=["POST"])
def crear():
    producto = Producto(contenido=request.form['contenido_producto'], categoria=request.form['categoria_producto'],
                        precio=request.form['precio_producto'], contador=0,stock=request.form['stock_producto'],total=0, hecha=True)
    db.session.add(producto)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/eliminar-producto/<id>')
def eliminar(id):
    producto = db.session.query(Producto).filter_by(id=int(id))
    producto.delete()
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/eliminar-usuario/<id>')
def eliminar_usuario(id):
    usuario = db.session.query(Registros).filter_by(id=int(id))
    usuario.delete()
    db.session.commit()
    return redirect(url_for('usuario'))


@app.route('/editar-producto/<id>')
def get_editar(id):
    product = db.session.query(Producto).filter_by(id=int(id)).first()
    return render_template("editar.html", product=product)


@app.route('/modificar/<id>', methods=["POST"])
def modificar(id):
    producto = db.session.query(Producto).filter_by(id=id).first()
    producto.contenido = request.form["editar-contenido"]
    producto.categoria = request.form["editar-categoria"]
    producto.precio = request.form["editar-precio"]
    producto.stock = request.form["editar-stock"]
    db.session.commit()
    db.session.close()
    return redirect(url_for('productos'))


admin = db.session.query(Registros).all()
for i in admin:
    if i.username == 'tokio':
        administrador = i.hecha=1
        db.session.commit()

if __name__ == '__main__':
    #db.Base.metadata.drop_all(bind=db.engine, checkfirst=True)
    db.Base.metadata.create_all(db.engine)
    app.run(debug=True)
