from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, jsonify
from flask_sqlalchemy import SQLAlchemy

from functools import wraps

import json
import folium

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_muy_segura'  # Cambia esto en producción

app.config['SQLALCHEMY_DATABASE_URI'] = \
    '{SGBD}://{usuario}:{clave}@{servidor}/{database}'.format(
        SGBD = 'mysql+mysqlconnector',
        usuario = 'brandonbozo',
        clave = 'mysqlroot',
        servidor = 'brandonbozo.mysql.pythonanywhere-services.com',
        database = 'brandonbozo$pedidoEntrega'
    )

db = SQLAlchemy(app)

class Usuarios(db.Model):
    nombre = db.Column(db.String(40),nullable=False )
    usuario = db.Column(db.String(20), primary_key=True)
    clave = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(80), nullable=False)


class Productos(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    articulo = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(100), nullable=False)
    precio_venta = db.Column(db.DECIMAL(9,2), nullable=False)
    stock_minimo = db.Column(db.Integer, nullable=False)
    existencia = db.Column(db.Integer, nullable=False)

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(40), nullable=False)
    correo = db.Column(db.String(80), nullable=False)
    local = db.Column(db.String(50), nullable=False)
    direc = db.Column(db.String(100), nullable=False)
    telf = db.Column(db.String(20), nullable=False)
    latitud = db.Column(db.DECIMAL(10,6))
    longitud = db.Column(db.DECIMAL(10,6))
    ciudad = db.Column(db.String(50), nullable=False)


class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    fecha = db.Column(db.Date, nullable=False)
    direccion = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    ciudad = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(20), nullable=False)

    cliente = db.relationship('Cliente')


class PedidoDetalle(db.Model):
    __tablename__ = 'pedido_detalle'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.DECIMAL(9,2), nullable=False)

    producto = db.relationship('Productos')



# Base de datos simulada de clientes
'''CLIENTES_DB = {
    "CLI001": {
        "codigo": "CLI001",
        "cliente": "Juan Pérez",
        "fecha": "2024-06-01",
        "direccion": "Av. Los Sauces # 345",
        "telefono": "7777 7777",
        "ciudad": "Cochabamba",
        "articulos": [
            {"id": 1, "nombre": "Laptop Dell", "cantidad": 2, "precio": 1200.00},
            {"id": 2, "nombre": "Mouse Inalámbrico", "cantidad": 5, "precio": 25.00},
            {"id": 3, "nombre": "Teclado Mecánico", "cantidad": 3, "precio": 80.00},
            {"id": 4, "nombre": "Monitor 24\"", "cantidad": 2, "precio": 300.00},
            {"id": 5, "nombre": "Webcam HD", "cantidad": 1, "precio": 150.00}
        ]
    },
    "CLI002": {
        "codigo": "CLID002",
        "cliente": "María García",
        "fecha": "2024-06-02",
        "direccion": "Av. Los Sauces # 345",
        "telefono": "7777 7777",
        "ciudad": "Cochabamba",
        "articulos": [
            {"id": 1, "nombre": "Smartphone Samsung", "cantidad": 1, "precio": 800.00},
            {"id": 2, "nombre": "Funda Protectora", "cantidad": 2, "precio": 15.00},
            {"id": 3, "nombre": "Cargador Rápido", "cantidad": 1, "precio": 35.00},
            {"id": 4, "nombre": "Auriculares Bluetooth", "cantidad": 1, "precio": 120.00},
            {"id": 5, "nombre": "Protector de Pantalla", "cantidad": 3, "precio": 10.00}
        ]
    },
    "CLI003": {
        "codigo": "CLI003",
        "cliente": "Carlos López",
        "fecha": "2024-06-03",
        "direccion": "Av. Los Sauces # 345",
        "telefono": "7777 7777",
        "ciudad": "Cochabamba",
        "articulos": [
            {"id": 1, "nombre": "Tablet iPad", "cantidad": 1, "precio": 600.00},
            {"id": 2, "nombre": "Apple Pencil", "cantidad": 1, "precio": 130.00},
            {"id": 3, "nombre": "Funda Smart Cover", "cantidad": 1, "precio": 45.00},
            {"id": 4, "nombre": "Adaptador USB-C", "cantidad": 2, "precio": 25.00},
            {"id": 5, "nombre": "Cable Lightning", "cantidad": 1, "precio": 20.00}
        ]
    }
}'''


# Base de datos simulada de pedidos
'''PEDIDOS_DB = {
    "PED001": {
        "numero": "PED001",
        "cliente": "Juan Pérez",
        "fecha": "2024-06-01",
        "direccion": "Av. Los Sauces # 345",
        "telefono": "7777 7777",
        "ciudad": "Cochabamba",
        "estado": "Pendiente",
        "articulos": [
            {"id": 1, "nombre": "Laptop Dell", "cantidad": 2, "precio": 1200.00},
            {"id": 2, "nombre": "Mouse Inalámbrico", "cantidad": 5, "precio": 25.00},
            {"id": 3, "nombre": "Teclado Mecánico", "cantidad": 3, "precio": 80.00},
            {"id": 4, "nombre": "Monitor 24\"", "cantidad": 2, "precio": 300.00},
            {"id": 5, "nombre": "Webcam HD", "cantidad": 1, "precio": 150.00}
        ]
    },
    "PED002": {
        "numero": "PED002",
        "cliente": "María García",
        "fecha": "2024-06-02",
        "direccion": "Av. Los Sauces # 345",
        "telefono": "7777 7777",
        "ciudad": "Cochabamba",
        "estado": "Pendiente",
        "articulos": [
            {"id": 1, "nombre": "Smartphone Samsung", "cantidad": 1, "precio": 800.00},
            {"id": 2, "nombre": "Funda Protectora", "cantidad": 2, "precio": 15.00},
            {"id": 3, "nombre": "Cargador Rápido", "cantidad": 1, "precio": 35.00},
            {"id": 4, "nombre": "Auriculares Bluetooth", "cantidad": 1, "precio": 120.00},
            {"id": 5, "nombre": "Protector de Pantalla", "cantidad": 3, "precio": 10.00}
        ]
    },
    "PED003": {
        "numero": "PED003",
        "cliente": "Carlos López",
        "fecha": "2024-06-03",
        "direccion": "Av. Los Sauces # 345",
        "telefono": "7777 7777",
        "ciudad": "Cochabamba",
        "estado": "Pendiente",
        "articulos": [
            {"id": 1, "nombre": "Tablet iPad", "cantidad": 1, "precio": 600.00},
            {"id": 2, "nombre": "Apple Pencil", "cantidad": 1, "precio": 130.00},
            {"id": 3, "nombre": "Funda Smart Cover", "cantidad": 1, "precio": 45.00},
            {"id": 4, "nombre": "Adaptador USB-C", "cantidad": 2, "precio": 25.00},
            {"id": 5, "nombre": "Cable Lightning", "cantidad": 1, "precio": 20.00}
        ]
    }
}'''


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Por favor, inicia sesión para acceder a esta página.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        #registro_usuario = Usuarios.query.filter_by(usuario=request.form['username']).first()

        # Buscar usuario con clave primaria = "johndoe"
        #usuario = Usuarios.query.get("seller3")
        registro_usuario = Usuarios.query.get(username)

        if not(registro_usuario):
            flash('Usuario o contraseña incorrectos', 'error')
            return render_template('login.html')

        usuario = registro_usuario.usuario

        if registro_usuario and registro_usuario.clave == password:
            session['username'] = username
            session['role'] = registro_usuario.role
            flash(f'Bienvenido, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash('Has cerrado sesión', 'info')
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
            'direccion': 'Calle La Tablada #4533',
            'telefono': '77788899',
            'pedido': '1001',
            'foto': 'tienda_barrio.jpg',
            'ubicacion': [-17.3935, -66.1570]
        },
        {
            'nombre': 'Abarrotes El Carmen',
            'contacto': 'Carmen Rojas',
            'direccion': 'Av. Blanco Galindo Km 2',
            'telefono': '76543210',
            'pedido': '1002',
            'foto': 'tienda_carmen.jpg',
            'ubicacion': [-17.3850, -66.1700]
        },
        {
            'nombre': 'Minimarket Los Andes',
            'contacto': 'Juan Mamani',
            'direccion': 'Av. América Este #345',
            'telefono': '70707070',
            'pedido': '1002',
            'foto': 'tienda_andes.jpg',
            'ubicacion': [-17.3980, -66.1420]
        },
        {
            'nombre': 'Tienda Don Pedro',
            'contacto': 'Pedro Flores',
            'direccion': 'Calle Jordán #1234',
            'telefono': '71234567',
            'pedido': '1003',
            'foto': 'tienda_pedro.jpg',
            'ubicacion': [-17.4050, -66.1610]
        },
        {
            'nombre': 'Mercadito Central',
            'contacto': 'María Gutiérrez',
            'direccion': 'Av. Ayacucho #887',
            'telefono': '78901234',
            'pedido': '1004',
            'foto': 'tienda_central.jpg',
            'ubicacion': [-17.3925, -66.1480]
        },
        {
            'nombre': 'Almacén El Sol',
            'contacto': 'Roberto Mendoza',
            'direccion': 'Av. Heroínas #765',
            'telefono': '76767676',
            'pedido': '1005',
            'foto': 'tienda_sol.jpg',
            'ubicacion': [-17.3880, -66.1550]
        },
        {
            'nombre': 'Tienda Doña Rosa',
            'contacto': 'Rosa Méndez',
            'direccion': 'Calle Hamiraya #432',
            'telefono': '79876543',
            'pedido': '1006',
            'foto': 'tienda_rosa.jpg',
            'ubicacion': [-17.4010, -66.1520]
        }
    ]

    # Agregar marcadores para cada tienda
    for tienda in tiendas:
        foto_url = url_for('static', filename='fotos/tienda_barrio.jpg')

        popup_content = f"""<table border=1 class="table table-success table-striped">
            <tr><td colspan="2"><img src='{ foto_url }' width='250' height='200'></td></tr>
            <tr><td>Tienda:</td><td>{ tienda['nombre'] }</td></tr>
            <tr><td>Contacto:</td><td>{ tienda['contacto'] }</td></tr>
            <tr><td>Dirección:</td><td>{ tienda['direccion'] }</td></tr>
            <tr><td>Teléfono:</td><td>{ tienda['telefono'] }</td></tr>
            <tr><td>Pedido:</td><td>{ tienda['pedido'] }</td></tr>
            <!--tr><td colspan="2"><center><a class="btn btn-primary" href="/pedido" style="color: white;">Ver Pedido</a></center></td></tr-->
            </table>"""

        folium.Marker(
            location=tienda['ubicacion'],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f'Tienda: {tienda["nombre"]}',
            icon=folium.Icon(color='blue', icon='shopping-cart', prefix='fa')
        ).add_to(m)

    # Guardar el mapa en un archivo HTML
    path='/home/brandonbozo/mysite/static/mapa_cbb.html'
    m.save(path)
    mapa_html = m._repr_html_()

    # Renderizar la plantilla HTML
    return render_template('mapa.html', mapa=mapa_html)


@app.route('/pedido')
def pedido():
    if 'username' not in session or session['role'] != 'driver':    ## == None:
        return redirect(url_for('login'))
    return render_template("pedido.html")


@app.route('/buscar_pedido', methods=['GET', 'POST'])
def buscar_pedido():
    pedido = None
    pedido_id = None
    error = None
    success = None
    total = 0

    if request.method == 'POST':
        pedido_id_input = request.form.get('pedido_id', '').strip()

        if not pedido_id_input.isdigit():
            error = "Ingrese un ID de pedido válido."
        else:
            pedido_db = Pedido.query.get(int(pedido_id_input))

            if not pedido_db:
                error = f"No existe el pedido con ID {pedido_id_input}"
            else:
                pedido_id = pedido_db.id  # 👈 ESTO ES CLAVE

                pedido = {
                    "cliente": pedido_db.cliente.nombre,
                    "telefono": pedido_db.cliente.telf,
                    "fecha": pedido_db.fecha,
                    "direccion": pedido_db.cliente.direc,
                    "ciudad": pedido_db.cliente.ciudad,
                    "estado": pedido_db.estado,
                    "articulos": []
                }

                total = 0
                for det in pedido_db.detalles:
                    subtotal = det.cantidad * det.precio
                    total += subtotal

                    pedido["articulos"].append({
                        "id": det.id,
                        "nombre": det.producto.articulo,
                        "cantidad": det.cantidad,
                        "precio": det.precio
                    })

                success = "Pedido encontrado correctamente."

    return render_template(
        "pedido.html",
        pedido=pedido,
        pedido_id=pedido_id,  # 👈 ESTO FALTABA
        total=total,
        error=error,
        success=success,
        pedidos_ejemplo=False
    )



@app.route('/actualizar_pedido', methods=['POST'])
def actualizar_pedido():
    numero_pedido = request.form.get('numero_pedido')

    if numero_pedido not in PEDIDOS_DB:
        return render_template('pedido.html',
                                    error="Pedido no encontrado.")

    # Actualizar artículos
    pedido = PEDIDOS_DB[numero_pedido]

    try:
        for articulo in pedido['articulos']:
            articulo_id = articulo['id']
            articulo['nombre'] = request.form.get(f'nombre_{articulo_id}', '').strip()
            articulo['cantidad'] = int(request.form.get(f'cantidad_{articulo_id}', 0))
            articulo['precio'] = float(request.form.get(f'precio_{articulo_id}', 0))

            # Validaciones básicas
            if not articulo['nombre']:
                raise ValueError("El nombre del artículo no puede estar vacío.")
            if articulo['cantidad'] <= 0:
                raise ValueError("La cantidad debe ser mayor a cero.")
            if articulo['precio'] < 0:
                raise ValueError("El precio no puede ser negativo.")

        # Calcular nuevo total
        total = sum(art['cantidad'] * art['precio'] for art in pedido['articulos'])

        return render_template('pedido.html',
                                    pedido=pedido,
                                    success="Pedido actualizado correctamente.",
                                    total=total)

    except (ValueError, TypeError) as e:
        return render_template('pedido2.html',
                                    pedido=pedido,
                                    error=f"Error al actualizar: {str(e)}",
                                    total=sum(art['cantidad'] * art['precio'] for art in pedido['articulos']))


@app.route('/preventa')
def preventa():
    if 'username' not in session or session['role'] != 'seller':
        return redirect(url_for('login'))
    productos = Productos.query.all()
    return render_template("preventa.html", productos = productos)

@app.route('/buscar_cliente', methods=['GET', 'POST'])
def buscar_cliente():
    codigo = None
    error = None
    success = None
    total = 0

    productos = Productos.query.all()

    if request.method == 'POST':
        codigo_cliente = request.form.get('codigo_cliente', '').strip()

        # Validar que sea numérico
        if not codigo_cliente.isdigit():
            error = "Ingrese un ID de cliente válido."
        else:
            cliente = Cliente.query.get(int(codigo_cliente))

            if not cliente:
                error = f"El cliente con ID {codigo_cliente} no existe."
            else:
                codigo = {
                    "codigo": cliente.id,
                    "cliente": cliente.nombre,
                    "telefono": cliente.telf,
                    "fecha": "",  # puedes poner date.today() si quieres
                    "direccion": cliente.direc,
                    "ciudad": cliente.ciudad,
                    "estado": "Activo"
                }

                success = "Cliente encontrado correctamente."

    return render_template(
        'preventa.html',
        codigo=codigo,
        error=error,
        success=success,
        total=total,
        clientes_ejemplo=False,
        productos=productos
    )



@app.route('/grabar_pedido', methods=['POST'])
def grabar_pedido():
    try:
        conn = mysql.connector.connect(
            host='brandonbozo.mysql.pythonanywhere-services.com',
            user='brandonbozo',
            password='mysqlroot',
            database='brandonbozo$pedidoEntrega'
        )
        cursor = conn.cursor(dictionary=True)

        # Cliente
        cliente_id = request.form.get('cliente_id')
        fecha = datetime.now().strftime('%Y-%m-%d')
        estado = 'Pendiente'

        # Crear pedido
        cursor.execute("""
            INSERT INTO pedido (cliente_id, fecha, estado, total)
            VALUES (%s, %s, %s, 0)
        """, (cliente_id, fecha, estado))

        pedido_id = cursor.lastrowid  # ID REAL DEL PEDIDO

        total_pedido = 0

        # Obtener productos
        cursor.execute("SELECT id, precio_venta FROM productos")
        productos = cursor.fetchall()

        for prod in productos:
            prod_id = prod['id']

            cantidad = request.form.get(f'cantidad_{prod_id}')
            precio = request.form.get(f'precio_{prod_id}')

            if cantidad and int(cantidad) > 0:
                cantidad = int(cantidad)
                precio = float(precio)
                subtotal = cantidad * precio
                total_pedido += subtotal

                # Insertar detalle
                cursor.execute("""
                    INSERT INTO pedido_detalle
                    (pedido_id, producto_id, cantidad, precio, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """, (pedido_id, prod_id, cantidad, precio, subtotal))

        # Actualizar total
        cursor.execute("""
            UPDATE pedido
            SET total = %s
            WHERE id = %s
        """, (total_pedido, pedido_id))

        conn.commit()

        return redirect(url_for(
            'preventa',
            success=f'Pedido #{pedido_id} guardado correctamente'
        ))

    except Exception as e:
        conn.rollback()
        return render_template(
            'preventa.html',
            error=f'Error al grabar pedido: {str(e)}'
        )

    finally:
        cursor.close()
        conn.close()


@app.route('/usuarios')
def index():
    if 'username' not in session or session['username'] == None:
        return redirect(url_for('login'))

    usuarios = Usuarios.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/agregar_usuario', methods=['GET', 'POST'])
def agregar_usuario():
    if request.method == 'POST':
        nuevo_usuario = Usuarios(
            nombre=request.form['nombre'],
            usuario=request.form['usuario'],
            clave=request.form['clave'],
            role=request.form['role'],
            correo=request.form['correo']
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        usuarios = Usuarios.query.all()
        return render_template('usuarios.html', usuarios=usuarios)
    return render_template('agregar_usuarios.html')


#@app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
@app.route('/editar_usuario/<id>', methods=['GET', 'POST'])
def editar_usuario(id):
    usuario = Usuarios.query.get(id)

    if request.method == 'POST':
        usuario.nombre = request.form['nombre']
        usuario.usuario = request.form['usuario']
        usuario.clave = request.form['clave']
        usuario.role = request.form['role']
        usuario.correo = request.form['correo']

        db.session.add(usuario)
        db.session.commit()

        usuarios = Usuarios.query.all()
        return render_template('usuarios.html', usuarios=usuarios)

    return render_template('editar_usuarios.html', usuario=usuario)


#@app.route('/eliminar_usuario/<int:id>')
@app.route('/eliminar_usuario/<id>')
def eliminar_usuario(id):
    usuario = Usuarios.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    usuarios = Usuarios.query.all()
    return render_template('usuarios.html', usuarios=usuarios)
