from flask import g, Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import folium
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'

app.config['DEBUG'] = True


try:
    connection = mysql.connector.connect(
        host='pythondevelop.mysql.pythonanywhere-services.com',
        user='pythondevelop',
        password='basededatos',
        database='pythondevelop$tiendas_movil'
    )
    print("Conexión exitosa a la base de datos")
except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if connection.is_connected():
        connection.close()


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://pythondevelop:basededatos@pythondevelop.mysql.pythonanywhere-services.com/pythondevelop$tiendas_movil'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'glugluglu'

db = SQLAlchemy(app)

#PRUEBAS DE BASE DE DATOS:
class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    usuario = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    clave = db.Column(db.String(255), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    rol = db.relationship('Rol', backref=db.backref('usuarios', lazy=True))

    def set_password(self, password):
        self.clave = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.clave, password)


class Categoria(db.Model):
    __tablename__ = 'categoria'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(50), nullable=True)

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=True)  # Nuevo campo añadido

    categoria = db.relationship('Categoria', backref=db.backref('productos', lazy=True))

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(100), nullable=False)
    razon_social = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    fecha_pedido = db.Column(db.Date, nullable=False)
    fecha_entrega = db.Column(db.Date, nullable=False)
    monto_total = db.Column(db.Float, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    usuario = db.relationship('Usuario', backref=db.backref('pedidos', lazy=True))


class ProductoPedido(db.Model):
    __tablename__ = 'productos_pedido'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    nombre_producto = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    pedido = db.relationship('Pedido', backref=db.backref('productos',lazy=True))

@app.after_request
def after_request(response):
    if hasattr(g, 'db_session'):
        g.db_session.remove()
    return response

@app.before_first_request
def crear_tablas():
    db.create_all()

@app.before_request
def before_request():
    if 'usuario' in session:
        g.usuario = Usuario.query.get(session['usuario'])
        if g.usuario:
            g.rol = Rol.query.get(g.usuario.rol_id)

@app.route('/registrar_usuario', methods=['GET', 'POST'])
def registrar_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        usuario = request.form['usuario']
        correo = request.form['correo']
        clave = request.form['clave']
        rol_id = request.form['rol']

        clave_encriptada = generate_password_hash(clave)

        try:
            nuevo_usuario = Usuario(nombre=nombre, usuario = usuario,correo=correo, clave=clave_encriptada, rol_id=rol_id)
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('Usuario registrado correctamente', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ocurrió un error: {str(e)}', 'danger')
            return redirect(url_for('registrar_usuario'))

    return render_template('registrar_usuario.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        clave = request.form['clave']

        usuario = Usuario.query.filter_by(correo=correo).first()

        if usuario and check_password_hash(usuario.clave, clave):
            session['usuario'] = usuario.id
            session['rol_id'] = usuario.rol_id
            flash('Inicio de sesión exitoso')
            return redirect(url_for('home'))
        else:
            flash('Usuario o contraseña incorrectos')

    return render_template('login.html')

#CODIGO NORMAL:
@app.route('/uploads', methods=['POST'])
def upload_file():
    try:
        if 'imageUpload' not in request.files:
            return 'No se ha encontrado la parte del archivo'
        file = request.files['imageUpload']
        if file.filename == '':
            return 'No se seleccionó ningún archivo'
        if file:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            return 'Archivo subido exitosamente'
    except Exception as e:
        return f'Ocurrió un error: {str(e)}'

@app.route('/')
def home():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    # Obtener el usuario de la sesión
    usuario = Usuario.query.get(session['usuario'])
    if usuario:  # Asegurarse de que el usuario existe
        rol = Rol.query.get(usuario.rol_id)
        return render_template('index.html', rol=rol)
    else:
        return redirect(url_for('login'))


@app.route('/registro_pedido', methods=['GET', 'POST'])
def registro_pedido():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para registrar un pedido', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        cliente = request.form['cliente']
        razon_social = request.form['razonSocial']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        fecha_pedido = request.form['fechaPedido']
        fecha_entrega = request.form['fechaEntrega']
        monto_total = request.form.get('montoTotal', 0.0)

        # Procesar productos dinámicos
        productos = request.form.getlist('productos[]')  # Lista de productos
        cantidades = request.form.getlist('cantidades[]')  # Lista de cantidades
        precios = request.form.getlist('precios[]')  # Lista de precios unitarios

        try:
            usuario_id = session['usuario']  # Usuario que hace el pedido
            nuevo_pedido = Pedido(
                cliente=cliente,
                razon_social=razon_social,
                direccion=direccion,
                telefono=telefono,
                fecha_pedido=fecha_pedido,
                fecha_entrega=fecha_entrega,
                monto_total=float(monto_total),
                usuario_id=usuario_id
            )
            db.session.add(nuevo_pedido)
            db.session.flush()  # Para obtener el ID del pedido recién creado

            # Guardar los productos relacionados
            for nombre, cantidad, precio in zip(productos, cantidades, precios):
                subtotal = int(cantidad) * float(precio)
                nuevo_producto = ProductoPedido(
                    pedido_id=nuevo_pedido.id,
                    nombre_producto=nombre,
                    cantidad=int(cantidad),
                    precio_unitario=float(precio),
                    subtotal=subtotal
                )
                db.session.add(nuevo_producto)

            db.session.commit()
            flash('Pedido registrado exitosamente', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ocurrió un error al registrar el pedido: {str(e)}', 'danger')
            return redirect(url_for('registro_pedido'))

    return render_template('pre-venta.html')

@app.route('/listar')
def listar_usuario():
    usuarios = Usuario.query.all()
    return render_template('listar.html', usuarios=usuarios)

@app.route('/listar_pedido')
def listar_pedido():
    pedidos = Pedido.query.all()
    return render_template('listar_pedido.html', pedidos= pedidos)

@app.route('/registro_clientes')
def registro_clientes():
    return render_template('registro_clientes.html')

@app.route('/productos', methods=['GET'])
def listar_productos():
    try:
        productos = Producto.query.all()
        return render_template('listar_productos.html', productos=productos)
    except Exception as e:
        return f"Error al listar productos: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/registro_productos', methods=['GET', 'POST'])
def registro_productos():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        categoria_id = int(request.form['categoria'])
        fecha_vencimiento = request.form['fecha_vencimiento'] or None
        precio_venta = float(request.form['precio_venta'])

        nuevo_producto = Producto(
            nombre=nombre,
            stock=cantidad,
            categoria_id=categoria_id,
            precio=precio_venta,
            fecha_vencimiento = fecha_vencimiento
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        flash('Producto registrado correctamente', 'success')
        return redirect(url_for('registro_productos'))

    categorias = Categoria.query.all()
    return render_template('registrar_productos.html', categorias=categorias)


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('home'))

@app.route('/ver_mapa')
def ver_mapa():
    # Generar el mapa centrado en una ubicación predeterminada
    m = folium.Map(location=[-17.3935, -66.1570], zoom_start=15)

    # Añadir puntos de tiendas como en tu código original
    tiendas = [
        {"nombre": "Doña Filomena", "ubicacion": [-17.3935, -66.1570], "contacto": "Filomena Delgado", "direccion": "calle La Tablada # 4533", "fecha": "10 Agosto 2024", "foto": "tienda_barrio.jpg"},
        {"nombre": "QR_Market", "ubicacion": [-17.373305, -66.158999], "contacto": "Juan Pérez", "direccion": "Av. Gualberto Villaroel", "fecha": "12 Septiembre 2024", "foto": "QR_Market.jpg"},
        {"nombre": "ECO_Pura", "ubicacion": [-17.374859, -66.160026], "contacto": "Maria Rosa", "direccion": "Calle La Tablada", "fecha": "12 Septiembre 2024", "foto": "tienda_barrio.jpg"}
    ]

    for tienda in tiendas:
        foto_url = url_for('static', filename=tienda['foto'])
        htmlcode = f"""
        <table border=1 class="table table-success table-striped">
            <tr><td colspan="2"><img src='{foto_url}' width='250' height='200'></td></tr>
            <tr><td>Tienda:</td><td>{tienda['nombre']}</td></tr>
            <tr><td>Contacto:</td><td>{tienda['contacto']}</td></tr>
            <tr><td>Dirección:</td><td>{tienda['direccion']}</td></tr>
            <tr><td>Fecha:</td><td>{tienda['fecha']}</td></tr>
        </table>"""

        folium.Marker(
            location=tienda['ubicacion'],
            popup=htmlcode,
            tooltip='Haz click para más información'
        ).add_to(m)

    mapa_html = m._repr_html_()
    return render_template('mapa.html', mapa=mapa_html)



if __name__ == '__main__':
    app.run(debug=True)
