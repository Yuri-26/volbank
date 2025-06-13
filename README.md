# 💳 VOLBANK - Banco Virtual Inteligente

**VOLBANK** es un banco virtual colombiano simulado que busca replicar el funcionamiento real de una institución financiera moderna. Este proyecto fue desarrollado como entrega final del curso de Analista de Datos y tiene como propósito demostrar habilidades técnicas en SQL, Python, modelado de datos, automatización, análisis de negocio y visualización con Power BI.

---

## 📌 Objetivo General

Desarrollar un ecosistema completo de un banco virtual, desde la creación de la base de datos, población realista de información, diseño de interfaces para usuarios y administradores, hasta la generación de dashboards interactivos para la toma de decisiones estratégicas.

---

## 🧱 Estructura del Proyecto

### 1. 🗂️ Modelo de Base de Datos (SQL)
- Script de creación de tablas relacionales: `Tablas_volbank.sql`
- Diagramas Entidad-Relación (ER) y modelo relacional
- Relaciones con claves primarias y foráneas
- Tablas principales:
  - `Clientes`, `Cuentas`, `Productos`, `Cartera`, `Morosidad`, `Transacciones`, `Tarjetas`
- Tablas de catálogo:
  - `TiposDocumento`, `TiposCuentaCatalogo`, `EstadosCuenta`, `TiposProductoCatalogo`, `EstadosMorosidad`, `TiposTarjeta`, `EstadosTarjeta`, `TiposTransaccion`

---

### 2. 🐍 Generación de Datos con Python – `Poblaciondatos.py`
- Uso de la librería `Faker` para poblar más de 8 tablas
- Conexión directa con MySQL para insertar los datos en tiempo real
- Datos simulados con lógica de negocio personalizada:
  - 91% de cuentas activas, 5% inactivas, 4% suspendidas
  - Morosidades distribuidas en distintos estados: pendiente, en proceso, cancelado, castigado
  - Canales de transacción distribuidos en proporción realista: Web, App, ATM
  - Productos más comunes: ahorro y crédito
  - Clientes con `CC` son siempre de Colombia

---

### 3. 🧑‍💼 Interfaz en Consola

#### `cliente_volbank.py` – Interfaz Cliente
- Registro de nuevo cliente directamente en la base de datos
- Inicio de sesión con número de documento y contraseña
- Menú interactivo:
  - Consultar cuentas (débito y crédito)
  - Consultar morosidad
  - Realizar transacción (transferencia o pago)
  - Salir
- Consultas con presentación en formato de tabla

#### `admin_volbank.py` – Interfaz Administrador
- Menú para personal autorizado
- Funciones:
  - Consultar cliente y sus cuentas
  - Actualizar información de cliente
  - Eliminar cliente
- Resultados tabulados para facilitar la lectura

---

### 4. 📊 Dashboard en Power BI – `Volbank.pbix`
- Conexión directa a MySQL
- Visualizaciones clave para análisis estratégico del negocio

#### 📄 Páginas del Dashboard
1. **Resumen General**
   - Total de clientes, productos, cuentas, transacciones
   - Morosidad activa vs total cartera

2. **Productos y Clientes**
   - Productos más adquiridos
   - Clientes con más de 2 productos
   - Segmentación por tipo de documento y nacionalidad

3. **Morosidad y Cartera**
   - Estados de morosidad: porcentaje y evolución por año
   - Saldos pendientes por estado
   - Comparativo por tipo de producto

4. **Transacciones y Canales**
   - Canales más usados por edad
   - Monto total de transacciones por tipo
   - Transacciones por tarjeta y saldo promedio

✅ Se emplearon medidas DAX, filtros por fecha y relaciones entre tablas.

---

## ⚙️ Requisitos Técnicos

### 🐍 Python 3.10+
  - Instalar dependencias necesarias:

```bash
pip install mysql-connector-python Faker
```
### 🐬 MySQL
  - Crear la base de datos volbank
  - Ejecutar el script Proyecto Banco.sql para crear todas las tablas y relaciones

### 📈 Power BI
  - Tener Power BI Desktop instalado en Windows
  - Conectar a la base de datos MySQL local
  - Abrir el archivo Volbank.pbix y actualizar las conexiones



##🚀 Cómo Ejecutar el Proyecto
  1. Crear la base de datos y las tablas con Proyecto Banco.sql
  2. Ejecutar Poblaciondatos.py para poblar los datos simulados
  3. Usar cliente_volbank.py o admin_volbank.py según el rol
  4. Abrir el archivo Volbank.pbix y actualizar las fuentes de datos para visualizar los dashboards



##🧠 Tecnologías Utilizadas
  - SQL – Modelado relacional y consultas de negocio
  - Python – Automatización, generación de datos y backend de interfaz
  - MySQL – Base de datos relacional
  - Faker – Simulación realista de datos
  - Power BI – Visualización y análisis de datos
  - GitHub – Control de versiones y documentación

