import mysql.connector
from faker import Faker
import random
from datetime import datetime, timedelta

# Conexión a la base de datos
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Yurany,1116",
    database="volbank"
)
cursor = cnx.cursor()

fake = Faker()

pk_lookup = {
    "TiposDocumento": "id_tipo_documento",
    "TiposCuentaCatalogo": "id_tipo_cuenta_catalogo",
    "EstadosCuenta": "id_estado_cuenta",
    "TiposProductoCatalogo": "id_tipo_producto_catalogo",
    "EstadosMorosidad": "id_estado_morosidad",
    "TiposTarjeta": "id_tipo_tarjeta",
    "EstadosTarjeta": "id_estado_tarjeta",
    "TiposTransaccion": "id_tipo_transaccion"
}

def obtener_ids(tabla):
    pk_col = pk_lookup[tabla]
    cursor.execute(f"SELECT {pk_col}, codigo FROM {tabla}")
    return cursor.fetchall()

def poblar_catalogos():
    # Llena tablas de búsqueda si están vacías
    catalogos = {
        "TiposDocumento": [("CC", "Cédula de Ciudadanía"), ("CE", "Cédula de Extranjería"), ("PAS", "Pasaporte")],
        "TiposCuentaCatalogo": [("Ahorro", "Cuenta de Ahorros"), ("Corriente", "Cuenta Corriente"), ("Credito", "Cuenta de Crédito"), ("Nomina", "Cuenta Nómina")],
        "EstadosCuenta": [("Activo", "Cuenta Activa"), ("Inactivo", "Cuenta Inactiva"), ("Suspendido", "Cuenta Suspendida")],
        "TiposProductoCatalogo": [("Ahorro", "Producto Cuenta Ahorros"), ("Corriente", "Producto Cuenta Corriente"), ("Credito", "Producto Crédito"), ("Inversion", "Producto Inversión")],
        "EstadosMorosidad": [("Pendiente", "Deuda Pendiente"), ("En proceso", "En proceso de cobro"), ("Cancelado", "Deuda Cancelada"), ("Castigado", "Deuda Castigada")],
        "TiposTarjeta": [("Debito", "Tarjeta Débito"), ("Credito", "Tarjeta Crédito")],
        "EstadosTarjeta": [("Activa", "Tarjeta Activa"), ("Bloqueada", "Tarjeta Bloqueada"), ("Expirada", "Tarjeta Expirada"), ("Cancelada", "Tarjeta Cancelada")],
        "TiposTransaccion": [("Debito", "Transacción Débito"), ("Credito", "Transacción Crédito"), ("Transferencia", "Transferencia"), ("Pago", "Pago")]
    }

    for tabla, valores in catalogos.items():
        pk_col = pk_lookup[tabla]
        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
        if cursor.fetchone()[0] == 0:  
            for codigo, descripcion in valores:
                cursor.execute(f"INSERT INTO {tabla} (codigo, descripcion) VALUES (%s, %s)", (codigo, descripcion))
            cnx.commit()

def poblar_direcciones(tipos_documento):
    direcciones_ids = []
    for tipo_doc_nombre in tipos_documento:
        if tipo_doc_nombre.lower() == "cc":
            pais = "Colombia"
        else:
            pais = fake.country()[:50]
        departamento = fake.state()[:50]
        ciudad = fake.city()[:50]
        nomenclatura = fake.address().replace("\n", ", ")[:100]
        cursor.execute(
            "INSERT INTO Direccion (pais, departamento, ciudad, nomenclatura) VALUES (%s, %s, %s, %s)",
            (pais, departamento, ciudad, nomenclatura)
        )
        direcciones_ids.append(cursor.lastrowid)
    cnx.commit()
    return direcciones_ids

def poblar_clientes(n=7582):
    tipos_doc = obtener_ids("TiposDocumento")
    tipos_doc_nombres = []
    tipos_doc_ids = []
    
    for _ in range(n):
        tipo_doc = random.choice(tipos_doc)
        tipos_doc_ids.append(tipo_doc[0])
        tipos_doc_nombres.append(tipo_doc[1])

    direcciones = poblar_direcciones(tipos_doc_nombres)
    
    clientes = []
    for i in range(n):
        tipo_doc_id = tipos_doc_ids[i]
        tipo_doc_nombre = tipos_doc_nombres[i].lower()

        if tipo_doc_nombre == "cc":
            numero_documento = fake.unique.numerify(text='##########')  
        elif tipo_doc_nombre == "ce":
            numero_documento = fake.unique.bothify(text='??######??') 
        else:
            numero_documento = fake.unique.numerify(text='##########')  
            
        nombre = fake.first_name()
        apellido = fake.last_name()
        fecha_nacimiento = fake.date_of_birth(minimum_age=18, maximum_age=90)
        id_direccion = direcciones[i]
        telefono = fake.phone_number()
        correo = fake.unique.email()
        contrasena = fake.password(length=10)
        fecha_vencimiento = None
        
        cursor.execute("""INSERT INTO Clientes (
                          numero_documento, id_tipo_documento, nombre, apellido, fecha_nacimiento, id_direccion, 
                          telefono, correo_electronico, contrasena, fecha_vencimiento)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                       (numero_documento, tipo_doc_id, nombre, apellido, fecha_nacimiento, id_direccion, telefono, correo, contrasena, fecha_vencimiento))
        clientes.append(numero_documento)
    cnx.commit()
    return clientes

def poblar_cuentas(clientes):
    tipos_cuenta = obtener_ids("TiposCuentaCatalogo")
    estados_cuenta = obtener_ids("EstadosCuenta")
    
    # Mapear códigos a IDs
    estado_ids = {codigo.lower(): id_estado for id_estado, codigo in estados_cuenta}
    id_activo = estado_ids["activo"]
    id_inactivo = estado_ids["inactivo"]
    id_suspendido = estado_ids["suspendido"]

    cuentas = []
    for cliente in clientes:
        for _ in range(random.randint(1, 3)):
            numero_cuenta = fake.unique.bban()[:20]
            tipo_cuenta_id = random.choice(tipos_cuenta)[0]
            saldo = round(random.uniform(0, 10000), 2)
            fecha_apertura = fake.date_between(start_date='-5y', end_date='today')
            
            # Asignación de estado con probabilidades específicas
            r = random.uniform(0, 1)
            if r < 0.91:
                estado_cuenta_id = id_activo
            elif r < 0.96:
                estado_cuenta_id = id_inactivo
            else:
                estado_cuenta_id = id_suspendido

            cursor.execute("""INSERT INTO Cuentas (
                              numero_cuenta, numero_documento_cliente, id_tipo_cuenta_catalogo, id_estado_cuenta, saldo, fecha_apertura)
                              VALUES (%s, %s, %s, %s, %s, %s)""",
                           (numero_cuenta, cliente, tipo_cuenta_id, estado_cuenta_id, saldo, fecha_apertura))
            cuentas.append(cursor.lastrowid)

    cnx.commit()
    return cuentas

def poblar_productos(clientes):
    tipos_producto = obtener_ids("TiposProductoCatalogo")
    # Mapear códigos a IDs
    tipo_dict = {codigo.lower(): id_ for id_, codigo in tipos_producto}
 
    # Porcentaje ponderado manual
    tipos_ponderados = (
        [tipo_dict["credito"]]   * 287 +
        [tipo_dict["inversion"]] * 421 +
        [tipo_dict["ahorro"]]    * 191 +
        [tipo_dict["corriente"]] * 101
    )
 
    productos = []
 
    for cliente in clientes:
        for _ in range(random.randint(1, 2)):  # Asignar 1 o 2 productos por cliente
            tipo_producto_id = random.choice(tipos_ponderados)
            descripcion = f"Producto {fake.word()} {fake.random_int(100, 999)}"
            fecha_adquisicion = fake.date_between(start_date='-5y', end_date='today')
            plazo = f"{random.choice([12, 24, 36, 48, 60])} meses"
            requisitos = "Ninguno"
            cursor.execute("""INSERT INTO Productos (
                                numero_documento_cliente, id_tipo_producto_catalogo, descripcion_producto, fecha_adquisicion, plazo, requisitos_especificos)
                              VALUES (%s, %s, %s, %s, %s, %s)""",
                           (cliente, tipo_producto_id, descripcion, fecha_adquisicion, plazo, requisitos))
            productos.append(cursor.lastrowid)
    cnx.commit()
    return productos

def poblar_cartera(clientes, productos):
    cartera_ids = []
    for cliente in clientes:
        prods_cliente = [p for p in productos if True]  
        for _ in range(random.randint(0,1)):
            if prods_cliente:
                producto_id = random.choice(prods_cliente)
            else:
                producto_id = None
            numero_contrato = fake.unique.bothify(text='CONTRATO-#####')
            saldo_actual = round(random.uniform(100, 5000), 2)
            saldo_pendiente = round(saldo_actual * random.uniform(0.1, 1), 2)
            fecha_vencimiento_credito = fake.date_between(start_date='today', end_date='+2y')
            fecha_proximo_pago = fake.date_between(start_date='today', end_date='+3m')
            tasa_interes = round(random.uniform(1.5, 10), 2)
            cursor.execute("""INSERT INTO Cartera (
                              id_producto, numero_contrato, numero_documento_cliente, saldo_actual, saldo_pendiente,
                              fecha_vencimiento_credito, fecha_proximo_pago, tasa_interes)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                           (producto_id, numero_contrato, cliente, saldo_actual, saldo_pendiente, fecha_vencimiento_credito, fecha_proximo_pago, tasa_interes))
            cartera_ids.append(cursor.lastrowid)
    cnx.commit()
    return cartera_ids

def poblar_morosidad(carteras):
    estados_morosidad = obtener_ids("EstadosMorosidad")
    estado_dict = {codigo.lower(): id_estado for id_estado, codigo in estados_morosidad}

    estado_ponderado = (
        [estado_dict["cancelado"]]  * 152 +
        [estado_dict["pendiente"]]  * 204 +
        [estado_dict["en proceso"]] * 451 +
        [estado_dict["castigado"]]  * 193
    )

    for cartera_id in carteras:
        monto_deuda = round(random.uniform(100, 5000), 2)
        dias_mora = random.randint(0, 120)
        estado_id = random.choice(estado_ponderado)
        historial = "No hay historial" if dias_mora < 30 else "Recuperación en proceso"

        fecha_inicio_mora = fake.date_between(
            start_date=datetime.strptime("2022-01-01", "%Y-%m-%d").date(),
            end_date=datetime.strptime("2025-12-31", "%Y-%m-%d").date()
        )

        cursor.execute("""INSERT INTO Morosidad (
                            id_cartera, monto_deuda, dias_mora, id_estado_morosidad, historial_recuperacion, fecha_inicio_mora)
                          VALUES (%s, %s, %s, %s, %s, %s)""",
                       (cartera_id, monto_deuda, dias_mora, estado_id, historial, fecha_inicio_mora))

    cnx.commit()

def poblar_tarjetas(cuentas):
    tipos_tarjeta = obtener_ids("TiposTarjeta")
    estados_tarjeta = obtener_ids("EstadosTarjeta")
    tarjetas = []
    for cuenta_id in cuentas:
        # Generar entre 0 y 2 tarjetas por cuenta
        for _ in range(random.randint(0, 2)):
            numero_tarjeta = fake.unique.credit_card_number()
            fecha_vencimiento = fake.date_between(start_date='today', end_date='+5y')
            tipo_tarjeta_id = random.choice(tipos_tarjeta)[0]
            estado_tarjeta_id = random.choice(estados_tarjeta)[0]
            cupo_asignado = round(random.uniform(1000, 20000), 2)
            fecha_emision = fake.date_between(start_date='-5y', end_date='today')
            cursor.execute("""INSERT INTO Tarjetas (numero_tarjeta, id_cuenta, id_tipo_tarjeta, id_estado_tarjeta,
                        cupo_asignado, fecha_emision, fecha_vencimiento_tarjeta) VALUES (%s, %s, %s, %s, %s, %s, %s)""", 
                        (numero_tarjeta, cuenta_id, tipo_tarjeta_id, estado_tarjeta_id,
                         cupo_asignado, fecha_emision, fecha_vencimiento)) 
            tarjetas.append(cursor.lastrowid)
    cnx.commit()
    return tarjetas

def poblar_transacciones(cuentas, tarjetas, n=15300):
    tipos_transaccion = obtener_ids("TiposTransaccion")  
    transacciones_creadas = 0
    transacciones = []

    # Mapear códigos a IDs
    pesos_transaccion = {
        'Debito': 0.5,
        'Credito': 0.25,
        'Transferencia': 0.15,
        'Pago': 0.10
    }
    tipo_codigo_list = list(pesos_transaccion.keys())
    cuentas_frecuentes = random.sample(cuentas, int(len(cuentas) * 0.25))  # 25% de cuentas con más movimiento

    for _ in range(n):
        # Dar preferencia a cuentas frecuentes
        if random.random() < 0.4:
            id_cuenta_origen = random.choice(cuentas_frecuentes)
        else:
            id_cuenta_origen = random.choice(cuentas)

        # Elegir tipo de transacción 
        tipo_codigo = random.choices(tipo_codigo_list, weights=pesos_transaccion.values(), k=1)[0]
        tipo_transaccion_id = next(id for id, cod in tipos_transaccion if cod == tipo_codigo)

        # Monto variable según tipo
        if tipo_codigo == "Credito":
            monto = round(random.uniform(5000, 20000), 2)
        elif tipo_codigo == "Transferencia":
            monto = round(random.uniform(100, 8000), 2)
        else:
            monto = round(random.uniform(10, 3000), 2)

        descripcion = fake.sentence(nb_words=6)
        referencia_transaccion = fake.unique.bothify(text="REF-##########")

        r_fecha = random.uniform(0, 1)
        if r_fecha < 0.7:
            fecha_hora = fake.date_time_between(start_date='-6m', end_date='now')
        else:
            fecha_hora = fake.date_time_between(start_date='-3y', end_date='-6m')

        # Canales 
        r_canal = random.uniform(0, 1)
        if r_canal < 0.5:
            canal = "App"
        elif r_canal < 0.85:
            canal = "Web"
        else:
            canal = "ATM"

        # Asegurar que cuenta destino no sea la misma
        posibles_destinos = [c for c in cuentas if c != id_cuenta_origen]
        id_cuenta_destino = random.choice(posibles_destinos) if posibles_destinos else id_cuenta_origen

        id_tarjeta = random.choice(tarjetas)

        cursor.execute("""INSERT INTO Transacciones (
                            fecha_hora, id_cuenta_origen, id_tipo_transaccion, monto, descripcion,
                            id_cuenta_destino, id_tarjeta, referencia_transaccion, canal)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                       (fecha_hora, id_cuenta_origen, tipo_transaccion_id, monto, descripcion,
                        id_cuenta_destino, id_tarjeta, referencia_transaccion, canal))
        transacciones_creadas += 1
        transacciones.append(cursor.lastrowid)

    cnx.commit()
    return transacciones

poblar_catalogos()

clientes = poblar_clientes(n=7582)
cuentas = poblar_cuentas(clientes)
productos = poblar_productos(clientes)
carteras = poblar_cartera(clientes, productos)
poblar_morosidad(carteras)
tarjetas = poblar_tarjetas(cuentas)
transacciones = poblar_transacciones(cuentas, tarjetas)


cursor.close()
cnx.close()