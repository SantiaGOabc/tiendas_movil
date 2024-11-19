import mysql.connector
from mysql.connector import errorcode

print("Conectando...")
try:
    conn = mysql.connector.connect(
           host='pythondevelop.mysql.pythonanywhere-services.com',
           user='pythondevelop',
           password='basededatos'
      )
except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('Existe un error en el nombre de usuario o en la clave')
      else:
            print(err)

cursor = conn.cursor()

cursor.execute("DROP DATABASE IF EXISTS `tiendas_movil`;")

cursor.execute("CREATE DATABASE `tiendas_movil`;")

cursor.execute("USE `tiendas_movil`;")

# creando las tablas
TABLES = {}

TABLES['Clientes'] = ('''
      CREATE TABLE `usuarios` (
      `nombre` varchar(40) NOT NULL,
      `usuario` varchar(20) NOT NULL,
      `clave` varchar(10) NOT NULL,
      `rol` varchar(10) NOT NULL,
      `correo` varchar(80) NOT NULL,
      PRIMARY KEY (`usuario`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

for cliente in TABLES:
      tabla_sql = TABLES[cliente]
      try:
            print('Creando tabla {}:'.format(cliente), end=' ')
            cursor.execute(tabla_sql)
      except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                  print('Ya existe la tabla')
            else:
                  print(err.msg)
      else:
            print('OK')

TABLES['Categorias'] = ('''
        CREATE TABLE categoria (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL
            )ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

for categoria in TABLES:
      tabla_sql = TABLES[categoria]
      try:
            print('Creando tabla {}:'.format(categoria), end=' ')
            cursor.execute(tabla_sql)
      except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                  print('Ya existe la tabla')
            else:
                  print(err.msg)
      else:
            print('OK')


TABLES['Productos'] = ('''
        CREATE TABLE `productos` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `nombre` VARCHAR(100) NOT NULL,
            `descripcion` TEXT,
            `precio` DECIMAL(10, 2) NOT NULL,
            `stock` INT NOT NULL,
            `categoria_id` INT,
            FOREIGN KEY (`categoria_id`) REFERENCES `categoria`(`id`)
                ON DELETE CASCADE
                ON UPDATE CASCADE
            )ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

for producto in TABLES:
      tabla_sql = TABLES[producto]
      try:
            print('Creando tabla {}:'.format(producto), end=' ')
            cursor.execute(tabla_sql)
      except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                  print('Ya existe la tabla')
            else:
                  print(err.msg)
      else:
            print('OK')


# commitando si no hay nada que tenga efecto
conn.commit()

cursor.close()
conn.close()