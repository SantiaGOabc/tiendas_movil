from flask import Flask, render_template, url_for, request, redirect, session, flash
import folium
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'glugluglu'

usuarios = {
    "usuario1": {"correo": "usuario1", "clave": "123", "rol": "vendedor"},
    "usuario2": {"correo": "usuario2", "clave": "456", "rol": "vendedor"},
    "usuario3": {"correo": "usuario3", "clave": "789", "rol": "gerente"}
}


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
    return render_template('index.html')

@app.route('/registro_clientes')
def registro_clientes():
    return render_template('registro_clientes.html')

@app.route('/registro_pedido')
def registro_pedido():
    return render_template('pre-venta.html')

@app.route('/registro_productos')
def registro_productos():
    return render_template('registrar_productos.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            correo = request.form['correo']
            clave = request.form['clave']

            for usuario, datos in usuarios.items():
                if datos['correo'] == correo and datos['clave'] == clave:
                    session['usuario'] = usuario
                    return redirect(url_for('home'))

            flash('Usuario o  contraseña incorrectas')
    except Exception as e:
        flash(f'Ocurrió un error: {str(e)}')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('home'))
@app.route('/ver_mapa')
def ver_mapa():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    m = folium.Map(location=[-17.3935, -66.1570], zoom_start=15)

    # TIENDA1
    tienda1 = {
        'nombre': 'Doña Filomena',
        'contacto': 'Filomena Delgado',
        'direccion': 'calle La Tablada # 4533',
        'fecha': '10 Agosto 2024',
        'foto': 'tienda_barrio.jpg',
        'ubicacion': [-17.3935, -66.1570]
    }

    # TIENDA2
    tienda2 = {
        'nombre': 'QR_Market',
        'contacto': 'Juan Pérez',
        'direccion': 'Av. Gualberto Villaroel',
        'fecha': '12 Septiembre 2024',
        'foto': 'QR_Market.jpg',
        'ubicacion': [-17.373305, -66.158999]
    }

    # TIENDA3
    tienda3 = {
        'nombre': 'ECO_Pura',
        'contacto': 'Maria Rosa',
        'direccion': 'Calle La Tablada',
        'fecha': '12 Septiembre 2024',
        'foto': 'tienda_barrio.jpg',
        'ubicacion': [-17.374859, -66.160026]
    }

    def agregar_tienda(tienda):
        foto_url = url_for('static', filename=tienda['foto'])
        htmlcode = f"""<table border=1 class="table table-success table-striped">
            <tr><td colspan="2"><img src='{foto_url}' width='250' height='200'></td></tr>
            <tr><td>Tienda:</td><td>{tienda['nombre']}</td></tr>
            <tr><td>Contacto:</td><td>{tienda['contacto']}</td></tr>
            <tr><td>Dirección:</td><td>{tienda['direccion']}</td></tr>
            <tr><td>Fecha:</td><td>{tienda['fecha']}</td></tr>
            <tr><td colspan="2"><center><a class="btn btn-primary" href={url_for('pedido')} style="color: white;">Hacer Pedido</a></center></td></tr>
            </table>"""

        folium.Marker(
            location=tienda['ubicacion'],
            popup=htmlcode,
            tooltip='Haz click para más información'
        ).add_to(m)

    agregar_tienda(tienda1)
    agregar_tienda(tienda2)
    agregar_tienda(tienda3)

    mapa_html = m._repr_html_()
    return render_template('mapa.html', mapa=mapa_html)

@app.route('/pedido')
def pedido():
    return render_template("ventana_modal.html")

if __name__ == '__main__':
    app.run(debug=True)