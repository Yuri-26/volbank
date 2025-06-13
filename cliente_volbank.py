import mysql.connector
from datetime import datetime
import random

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Yurany,1116",
        database="volbank"
    )

def consultar_cuentas(cliente_doc):
    cnx = conectar()
    cursor = cnx.cursor()
    cursor.execute("""
        SELECT c.numero_cuenta, tcc.codigo AS tipo_cuenta, c.saldo, ec.codigo AS estado
        FROM Cuentas c
        JOIN TiposCuentaCatalogo tcc ON c.id_tipo_cuenta_catalogo = tcc.id_tipo_cuenta_catalogo
        JOIN EstadosCuenta ec ON c.id_estado_cuenta = ec.id_estado_cuenta
        WHERE c.numero_documento_cliente = %s
    """, (cliente_doc,))

    cuentas = cursor.fetchall()
    if cuentas:
        print("\n--- Cuentas Asociadas ---")
        print("{:<20} {:<15} {:<12} {:<12}".format("Número de Cuenta", "Tipo", "Saldo", "Estado"))
        print("-" * 60)
        for cuenta in cuentas:
            print("{:<20} {:<15} {:<12,.2f} {:<12}".format(cuenta[0], cuenta[1], cuenta[2], cuenta[3]))
    else:
        print("No se encontraron cuentas asociadas a este cliente.")

    cursor.close()

def consultar_morosidad(cliente_doc):
    cnx = conectar()
    cursor = cnx.cursor()
    cursor.execute("""
        SELECT m.id_cartera, m.monto_deuda, m.dias_mora, em.codigo AS estado,
               m.historial_recuperacion
        FROM Morosidad m
        JOIN Cartera c ON m.id_cartera = c.id_cartera
        JOIN EstadosMorosidad em ON m.id_estado_morosidad = em.id_estado_morosidad
        WHERE c.numero_documento_cliente = %s
    """, (cliente_doc,))
    
    morosidades = cursor.fetchall()
    if morosidades:
        print("\n--- Morosidades Asociadas ---")
        print("{:<10} {:<12} {:<10} {:<15} {:<25}".format(
            "ID", "Deuda ($)", "Días", "Estado", "Historial"
        ))
        print("-" * 85)
        for m in morosidades:
            print("{:<10} {:<12,.2f} {:<10} {:<15} {:<25}".format(
                m[0], m[1], m[2], m[3], m[4][:24]
            ))
    else:
        print("No se encontraron registros de morosidad.")

    cursor.close()
    cnx.close()

def realizar_transaccion(cliente_doc):
    cnx = conectar()
    cursor = cnx.cursor()
    id_cuenta_origen = int(input("ID de cuenta origen: "))
    id_cuenta_destino = int(input("ID de cuenta destino: "))
    monto = float(input("Monto: "))
    tipo_transaccion = int(input("ID tipo transacción (1: Débito, 2: Crédito, etc.): "))
    id_tarjeta = int(input("ID de tarjeta asociada (opcional): ") or 1)
    canal = input("Canal (ATM/Web/App): ")
    referencia = "REF-" + str(random.randint(10000000, 99999999))
    descripcion = input("Descripción: ")

    cursor.execute("""INSERT INTO Transacciones (
        fecha_hora, id_cuenta_origen, id_tipo_transaccion, monto, descripcion,
        id_cuenta_destino, id_tarjeta, referencia_transaccion, canal)
        VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s)
    """, (id_cuenta_origen, tipo_transaccion, monto, descripcion,
          id_cuenta_destino, id_tarjeta, referencia, canal))

    cnx.commit()
    print("Transacción registrada.")
    cursor.close()
    cnx.close()

def login_cliente():
    doc = input("¡Hola, Bienvenido a Volbank! \nPara iniciar sesión ingresa el número de documento y la contraseña del usuario. \nNúmero de documento: ")
    password = input("Ingresa por favor la contraseña. \nContraseña: ")
    cnx = conectar()
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM Clientes WHERE numero_documento = %s AND contrasena = %s", (doc, password))
    cliente = cursor.fetchone()
    cursor.close()
    cnx.close()
    return cliente

def menu_cliente():
    cliente = login_cliente()
    if not cliente:
        print("Credenciales incorrectas. \nLo sentimos, revisa la contraseña ingresada.")
        return
    
    cliente_doc = cliente[0]
    while True:
        print("\n--- MENÚ CLIENTE ---\nEn nuestro menú de clientes podrás encontrar las siguientes opciones:")
        print("1. Consultar cuentas")
        print("2. Consultar morosidad")
        print("3. Realizar transacción")
        print("4. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            consultar_cuentas(cliente_doc)
        elif opcion == "2":
            consultar_morosidad(cliente_doc)
        elif opcion == "3":
            realizar_transaccion(cliente_doc)
        elif opcion == "4":
            break
        else:
            print("Opción inválida.")


menu_cliente()
