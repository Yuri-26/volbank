CREATE DATABASE IF NOT EXISTS volbank;
USE volbank;

-- TABLAS DE BÚSQUEDA (LOOKUP TABLES) --

-- Para Clientes.tipo_documento
CREATE TABLE TiposDocumento (
    id_tipo_documento INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(10) UNIQUE NOT NULL, -- CC, CE, Pasaporte
    descripcion VARCHAR(100) NOT NULL
);

-- Para Cuentas.tipo_cuenta (antes TipoCuenta.tipo_cuenta)
CREATE TABLE TiposCuentaCatalogo (
    id_tipo_cuenta_catalogo INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL, -- Ahorro, Corriente, Credito, Nomina
    descripcion VARCHAR(100) NOT NULL
);

-- Para Cuentas.estado (antes TipoCuenta.estado)
CREATE TABLE EstadosCuenta (
    id_estado_cuenta INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL, -- Activo, Inactivo, Suspendido
    descripcion VARCHAR(100) NOT NULL
);

-- Para Productos.tipos_productos
CREATE TABLE TiposProductoCatalogo (
    id_tipo_producto_catalogo INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL, -- Cuenta Ahorros, Cuenta Corriente, Credito, Inversion
    descripcion VARCHAR(100) NOT NULL
);

-- Para Morosidad.estado
CREATE TABLE EstadosMorosidad (
    id_estado_morosidad INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL, -- Pendiente, En proceso, Cancelado, Castigado
    descripcion VARCHAR(100) NOT NULL
);

-- Para Tarjetas.tipo_tarjeta
CREATE TABLE TiposTarjeta (
    id_tipo_tarjeta INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL, -- Debito, Credito
    descripcion VARCHAR(100) NOT NULL
);

-- Para Tarjetas.estado
CREATE TABLE EstadosTarjeta (
    id_estado_tarjeta INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL, -- Activa, Bloqueada, Expirada, Cancelada
    descripcion VARCHAR(100) NOT NULL
);

-- Para Transacciones.tipo_transaccion
CREATE TABLE TiposTransaccion (
    id_tipo_transaccion INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(30) UNIQUE NOT NULL, -- Debito, Credito, Transferencia, Pago
    descripcion VARCHAR(100) NOT NULL
);


-- TABLAS PRINCIPALES --

-- Tabla Dirección
CREATE TABLE Direccion (
    id_direccion INT AUTO_INCREMENT PRIMARY KEY,
    pais VARCHAR(50) NOT NULL,
    departamento VARCHAR(50) NOT NULL,
    ciudad VARCHAR(50) NOT NULL,
    nomenclatura VARCHAR(200) NOT NULL -- Dirección detallada
);

-- Tabla Clientes
CREATE TABLE Clientes (
    numero_documento VARCHAR(50) PRIMARY KEY, -- Cambiado a VARCHAR para flexibilidad (ej. pasaportes con letras)
    id_tipo_documento INT NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    apellido VARCHAR(255) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    id_direccion INT NOT NULL,
    telefono VARCHAR(30) NOT NULL, -- Aumentado por si acaso
    correo_electronico VARCHAR(255) UNIQUE NOT NULL, -- Añadida restricción UNIQUE
    contrasena VARCHAR(255) NOT NULL, -- Hashear en la aplicación
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Cambiado a DATETIME para más precisión y valor por defecto
    fecha_vencimiento DATE, -- Considerar si este campo es necesario aquí o en una tabla de productos/membresías
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_tipo_documento) REFERENCES TiposDocumento(id_tipo_documento),
    FOREIGN KEY (id_direccion) REFERENCES Direccion(id_direccion)
    -- El índice explícito para numero_documento no es necesario ya que es PRIMARY KEY.
);

-- Tabla Cuentas (antes TipoCuenta)
CREATE TABLE Cuentas (
    id_cuenta INT AUTO_INCREMENT PRIMARY KEY,
    numero_cuenta VARCHAR(50) UNIQUE NOT NULL, -- Número de cuenta bancaria real, debe ser único
    numero_documento_cliente VARCHAR(50) NOT NULL, -- VINCULO A CLIENTES
    id_tipo_cuenta_catalogo INT NOT NULL,
    id_estado_cuenta INT NOT NULL,
    saldo DECIMAL(15, 2) NOT NULL DEFAULT 0.00, -- Añadido saldo a la cuenta
    fecha_apertura DATE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (numero_documento_cliente) REFERENCES Clientes(numero_documento),
    FOREIGN KEY (id_tipo_cuenta_catalogo) REFERENCES TiposCuentaCatalogo(id_tipo_cuenta_catalogo),
    FOREIGN KEY (id_estado_cuenta) REFERENCES EstadosCuenta(id_estado_cuenta),
    INDEX idx_cuenta_cliente (numero_documento_cliente) -- Índice para búsquedas por cliente
);

-- Tabla Productos (Representa productos específicos adquiridos por el cliente)
CREATE TABLE Productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    numero_documento_cliente VARCHAR(50) NOT NULL,
    id_tipo_producto_catalogo INT NOT NULL,
    descripcion_producto VARCHAR(255) NOT NULL, -- Ej: "Préstamo Personal Auto", "Fondo de Inversión XYZ"
    fecha_adquisicion DATE NOT NULL,
    plazo VARCHAR(50), -- Ej: "36 meses", "Indefinido"
    requisitos_especificos TEXT, -- Requisitos o condiciones particulares de esta adquisición
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (numero_documento_cliente) REFERENCES Clientes(numero_documento),
    FOREIGN KEY (id_tipo_producto_catalogo) REFERENCES TiposProductoCatalogo(id_tipo_producto_catalogo),
    INDEX idx_producto_cliente (numero_documento_cliente)
);

-- Tabla producto_cuenta_asociacion (antes producto_tipocuenta, relación muchos a muchos)
-- Asocia un producto adquirido específico con una o más cuentas del cliente.
-- Ej: Un préstamo (producto) se desembolsa en una cuenta de ahorros (cuenta).
CREATE TABLE Producto_Cuenta_Asociacion (
    id_producto_cuenta_asociacion INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    id_cuenta INT NOT NULL, -- Referencia a la tabla Cuentas
    rol_cuenta VARCHAR(100), -- Ej: 'Cuenta de Desembolso', 'Cuenta de Débito Automático'
    fecha_asociacion DATE NOT NULL DEFAULT (CURRENT_DATE),
    detalles VARCHAR(255),
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto),
    FOREIGN KEY (id_cuenta) REFERENCES Cuentas(id_cuenta),
    UNIQUE KEY uq_producto_cuenta_rol (id_producto, id_cuenta, rol_cuenta) -- Evita duplicados
);

-- Tabla Cartera (Gestión de deudas o créditos específicos)
CREATE TABLE Cartera (
    id_cartera INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT, -- Opcional: Enlaza directamente al producto de crédito que originó esta cartera. Puede ser NULL si la cartera no se origina de un 'Producto'.
    numero_contrato VARCHAR(50) UNIQUE NOT NULL, -- Número de contrato del crédito/deuda
    numero_documento_cliente VARCHAR(50) NOT NULL, -- Cliente responsable de esta cartera
    saldo_actual DECIMAL(12, 2) NOT NULL,
    saldo_pendiente DECIMAL(12, 2) NOT NULL,
    fecha_vencimiento_credito DATE NOT NULL, -- Fecha final del crédito/deuda
    fecha_proximo_pago DATE,
    tasa_interes DECIMAL(5,2),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (numero_documento_cliente) REFERENCES Clientes(numero_documento),
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto),
    INDEX idx_cartera_cliente (numero_documento_cliente)
);

-- Tabla Morosidad
CREATE TABLE Morosidad (
    id_morosidad INT AUTO_INCREMENT PRIMARY KEY,
    id_cartera INT NOT NULL,
    -- id_producto INT NOT NULL, -- Considerar si es necesario si id_cartera ya puede enlazar a un producto
    monto_deuda DECIMAL(12, 2) NOT NULL,
    dias_mora INT NOT NULL,
    id_estado_morosidad INT NOT NULL,
    historial_recuperacion TEXT,
    fecha_inicio_mora DATE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cartera) REFERENCES Cartera(id_cartera),
    FOREIGN KEY (id_estado_morosidad) REFERENCES EstadosMorosidad(id_estado_morosidad)
    -- Si se mantiene id_producto: FOREIGN KEY (id_producto) REFERENCES Productos(id_producto)
);

-- Tabla Tarjetas
CREATE TABLE Tarjetas (
    id_tarjeta INT AUTO_INCREMENT PRIMARY KEY,
    numero_tarjeta VARCHAR(20) UNIQUE NOT NULL, -- Generalmente 16-19 dígitos
    fecha_vencimiento_tarjeta DATE NOT NULL, -- Renombrado para claridad
    -- CVV NO DEBE ALMACENARSE --
    id_tipo_tarjeta INT NOT NULL,
    id_estado_tarjeta INT NOT NULL,
    id_cuenta INT NOT NULL, -- Cuenta principal asociada a la tarjeta
    cupo_asignado DECIMAL(12, 2) NULL, -- Para tarjetas de crédito
    fecha_emision DATE NOT NULL DEFAULT (CURRENT_DATE),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_tipo_tarjeta) REFERENCES TiposTarjeta(id_tipo_tarjeta),
    FOREIGN KEY (id_estado_tarjeta) REFERENCES EstadosTarjeta(id_estado_tarjeta),
    FOREIGN KEY (id_cuenta) REFERENCES Cuentas(id_cuenta)
);

-- Tabla Transacciones
CREATE TABLE Transacciones (
    id_transaccion INT AUTO_INCREMENT PRIMARY KEY,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_cuenta_origen INT NOT NULL, -- Cuenta desde la que se origina la transacción
    id_tipo_transaccion INT NOT NULL,
    monto DECIMAL(12, 2) NOT NULL,
    descripcion VARCHAR(255),
    id_cuenta_destino INT NULL, -- Cuenta destino (para transferencias)
    id_tarjeta INT NULL, -- Tarjeta utilizada (si aplica), ahora NULLABLE
    referencia_transaccion VARCHAR(100) UNIQUE, -- Referencia única para la transacción, puede ser generada
    canal VARCHAR(50), -- Ej: 'ATM', 'Web', 'App', 'Sucursal'
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- Útil si la transacción tiene estados (ej. pendiente, confirmada)
    FOREIGN KEY (id_cuenta_origen) REFERENCES Cuentas(id_cuenta),
    FOREIGN KEY (id_tipo_transaccion) REFERENCES TiposTransaccion(id_tipo_transaccion),
    FOREIGN KEY (id_cuenta_destino) REFERENCES Cuentas(id_cuenta),
    FOREIGN KEY (id_tarjeta) REFERENCES Tarjetas(id_tarjeta)
);