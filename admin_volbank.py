import mysql.connector

# Conexión a la base de datos
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Yurany,1116",
    database="volbank"
)
cursor = cnx.cursor()

def consultar_cliente(cursor):
    documento = input("Documento del cliente: ")

    # Obtener datos del cliente
    cursor.execute("""
        SELECT nombre, apellido, correo_electronico, telefono
        FROM Clientes
        WHERE numero_documento = %s
    """, (documento,))
    cliente = cursor.fetchone()

    if cliente:
        print(f"\n--- Información del Cliente ---")
        print(f"Nombre: {cliente[0]} {cliente[1]}")
        print(f"Correo: {cliente[2]}")
        print(f"Teléfono: {cliente[3]}\n")

        # Mostrar cuentas
        cursor.execute("""
            SELECT c.numero_cuenta, tcc.codigo AS tipo, c.saldo, ec.codigo AS estado
            FROM Cuentas c
            JOIN TiposCuentaCatalogo tcc ON c.id_tipo_cuenta_catalogo = tcc.id_tipo_cuenta_catalogo
            JOIN EstadosCuenta ec ON c.id_estado_cuenta = ec.id_estado_cuenta
            WHERE c.numero_documento_cliente = %s
        """, (documento,))
        cuentas = cursor.fetchall()

        if cuentas:
            print("--- Cuentas Asociadas ---")
            print("{:<20} {:<15} {:<12} {:<12}".format("Número de Cuenta", "Tipo", "Saldo", "Estado"))
            print("-" * 60)
            for cuenta in cuentas:
                print("{:<20} {:<15} {:<12,.2f} {:<12}".format(cuenta[0], cuenta[1], float(cuenta[2]), cuenta[3]))
        else:
            print("Este cliente no tiene cuentas registradas.")
    else:
        print("\nCliente no encontrado.\n")

def actualizar_cliente(cursor):
    documento = input("Documento del cliente a actualizar: ")
    campo = input("Campo a actualizar (nombre, apellido, correo_electronico, telefono): ")
    nuevo_valor = input(f"Nuevo valor para {campo}: ")

    if campo not in ["nombre", "apellido", "correo_electronico", "telefono"]:
        print("Campo inválido.")
        return

    query = f"UPDATE Clientes SET {campo} = %s WHERE numero_documento = %s"
    cursor.execute(query, (nuevo_valor, documento))
    cnx.commit()
    print("Cliente actualizado exitosamente.")

def eliminar_cliente(cursor):
    documento = input("Documento del cliente a eliminar: ")
    cursor.execute("DELETE FROM Clientes WHERE numero_documento = %s", (documento,))
    cnx.commit()
    print("Cliente eliminado correctamente.")

def menu_admin():
    print("\n¡Hola, Bienvenido al portal administrativo de Volbank!")
    while True:
        print("""
--- MENÚ ADMINISTRADOR ---
Acontinuación encontrarás las opciones de nuestro menú para colaboradores:
1. Consultar cliente
2. Actualizar cliente
3. Eliminar cliente
4. Salir
        """)
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            consultar_cliente(cursor)
        elif opcion == "2":
            actualizar_cliente(cursor)
        elif opcion == "3":
            eliminar_cliente(cursor)
        elif opcion == "4":
            print("Gracias por utilizar el sistema administrativo de Volbank.")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    menu_admin()
    cursor.close()
    cnx.close()
