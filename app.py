from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps

import json
import folium

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_muy_segura' # Cambia esto en producción

# Simulación de una base de datos de usuarios
users = {
    'admin': {'password': 'adminpass', 'role': 'admin'},
    'driver': {'password': 'driverpass', 'role': 'driver'},
    'editor': {'password': 'editorpass', 'role': 'editor'}
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Por favor, inicia sesión para acceder a esta página.', 'error')
            return redirect(url_for('login'))
        return decorated_function(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['role'] = users[username]['role']
            flash(f'Bienvenido, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/ver_mapa')
def ver_mapa():
    if 'username' not in session or session['username'] == None:
        return redirect(url_for('login'))

    # Crear el mapa centrado en Cochabamba
    m = folium.Map(location=[-17.3935, -66.1570], zoom_start=15)

    # Lista de tiendas con sus datos
    tiendas = [
        {
            'nombre': 'Doña Filomena',
            'contacto': 'Filomena Delgado',
            'direccion': 'Calle la Tablada #4533',
            'telefono': '77788899',
            'foto': 'tienda_barrio.jpg',
            'ubicacion': [-17.3910, -66.1570]
        },
        {
            'nombre': 'Abarrotes El Carmen',
            'contacto': 'Carmen Rojas',
            'direccion': 'Av. Blanco Galindo Km 2',
            'telefono': '76543210',
            'foto': 'tienda_carmen.jpg',
            'ubicacion': [-17.3850, -66.1700]
        },
        {
            'nombre': 'Minimarket Los Andes',
            'contacto': 'Juan Mamani',
            'direccion': 'Av. América Este #345',
            'telefono': '76707070',
            'foto': 'tienda_andes.jpg',
            'ubicacion': [-17.3980, -66.1420]
        },
        {
            'nombre': 'Tienda Don Pedro',
            'contacto': 'Pedro Flores',
            'direccion': 'Calle Jordan #1234',
            'telefono': '72334567',
            'foto': 'tienda_pedro.jpg',
            'ubicacion': [-17.4050, -66.1610]
        },
        {
            'nombre': 'Mercadito Central',
            'contacto': 'María Gutiérrez',
            'direccion': 'Av. Ayacucho #887',
            'telefono': '78901234',
            'foto': 'tienda_central.jpg',
            'ubicacion': [-17.3925, -66.1480]
        },
        {
            'nombre': 'Almacén El Sol',
            'contacto': 'Roberto Mendoza',
            'direccion': 'Av. Heroinas #765',
            'telefono': '76767676',
            'foto': 'tienda_sol.jpg',
            'ubicacion': [-17.3880, -66.1550]
        },
        {
            'nombre': 'Tienda Doña Rosa',
            'contacto': 'Rosa Méndez',
            'direccion': 'Calle Ramiraya #432',
            'telefono': '79876543',
            'foto': 'tienda_rosa.jpg',
            'ubicacion': [-17.4010, -66.1520]
        }
    ]

    # Agregar marcadores para cada tienda
    for tienda in tiendas:
        foto_url = url_for('static', filename=f'fotos/{tienda["foto"]}')
        popup_content = f"""<table border=1 class="table table-success table-striped">
        <tr><td colspan="2"><img src="{foto_url}" width='250' height='200'></td></tr>
        <tr><td>Tienda:</td><td><b>{tienda['nombre']}</b></td></tr>
        <tr><td>Contacto:</td><td><b>{tienda['contacto']}</b></td></tr>
        <tr><td>Dirección:</td><td><b>{tienda['direccion']}</b></td></tr>
        <tr><td>Teléfono:</td><td><b>{tienda['telefono']}</b></td></tr>
        <tr><td colspan="2"><center><a class="btn btn-primary" href="/pedido"
        style="color: white">Ver Pedido/a</center></td></tr>
        </table>"""

        folium.Marker(
            location=tienda['ubicacion'],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f'Tienda: {tienda["nombre"]}',
            icon=folium.Icon(color='blue', icon='shopping-cart', prefix='fa')
        ).add_to(m)

    # Guardar el mapa en un archivo HTML
    path='/home/lamateria/mysite/static/mapa_cbb.html'
    # path='savedPath'
    mape_html = m._repr_html_()

    # Renderizar la plantilla HTML
    return render_template('mapa.html', mapa=mape_html)


@app.route('/pedido')
def pedido():
    if 'username' not in session or session['username'] == None:
        return redirect(url_for('login'))

    return render_template("pedido.html")