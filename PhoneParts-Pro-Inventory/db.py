# © 2025 Kener Cartagena. Todos los derechos reservados.
# Uso personal únicamente. Prohibida su distribución sin permiso.
from tkinter import messagebox
import mysql.connector

class Producto:
    def __init__(self, id_producto, nombre, marca, descripcion, precio, stock):
        self.id_producto = id_producto
        self.nombre = nombre
        self.marca = marca
        self.descripcion = descripcion
        self.precio = precio
        self.stock = stock

    def __str__(self):
        return f"{self.nombre} ({self.marca}) - Stock: {self.stock}"

class DatabaseManager:
    def __init__(self, host, user, password, database_name):
        self.host = host
        self.user = user
        self.password = password
        self.database_name = database_name
        self.connection = None
        self.cursor = None

    def conectar(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database_name,
                auth_plugin='mysql_native_password'
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print("Conexión a MySQL exitosa.")
            self._crear_tabla_si_no_existe()
            return True
        except mysql.connector.Error as err:
            print(f"Error al conectar a MySQL: {err}")
            messagebox.showerror("Error de Base de Datos", f"No se pudo conectar a la base de datos: {err}\nPor favor, verifica la configuración y que el servidor MySQL esté en ejecución.")
            return False

    def _crear_tabla_si_no_existe(self):
        query = """
        CREATE TABLE IF NOT EXISTS productos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            marca VARCHAR(100),
            descripcion TEXT,
            precio DECIMAL(10, 2) NOT NULL,
            stock INT NOT NULL
        )
        """
        try:
            if not self.cursor:
                print("Error: Cursor no inicializado antes de crear tabla.")
                return
            self.cursor.execute(query)
            self.connection.commit()
            print("Tabla 'productos' verificada/creada.")
        except mysql.connector.Error as err:
            print(f"Error al crear la tabla: {err}")

    def obtener_productos(self, nombre_buscar=None, marca_buscar=None):
        if not self.cursor:
            print("No hay cursor de base de datos.")
            messagebox.showerror("Error de Base de Datos", "No hay conexión activa para obtener productos.")
            return []
        
        query = "SELECT * FROM productos WHERE stock > 0"
        params = []
        if nombre_buscar:
            query += " AND nombre LIKE %s"
            params.append(f"%{nombre_buscar}%")
        if marca_buscar and marca_buscar != "Todas":
            query += " AND marca = %s"
            params.append(marca_buscar)
        
        try:
            self.cursor.execute(query, params)
            productos_data = self.cursor.fetchall()
            return [Producto(p['id'], p['nombre'], p['marca'], p['descripcion'], p['precio'], p['stock']) for p in productos_data]
        except mysql.connector.Error as err:
            print(f"Error al obtener productos: {err}")
            messagebox.showerror("Error de Base de Datos", f"Error al leer productos: {err}")
            return []

    def agregar_producto(self, producto):
        if not self.cursor:
            print("No hay cursor de base de datos.")
            messagebox.showerror("Error de Base de Datos", "No hay conexión activa para agregar el producto.")
            return False
        
        query = """
        INSERT INTO productos (nombre, marca, descripcion, precio, stock) 
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (producto.nombre, producto.marca, producto.descripcion, producto.precio, producto.stock)
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            producto.id_producto = self.cursor.lastrowid
            print(f"Producto '{producto.nombre}' agregado con ID: {producto.id_producto}.")
            return True
        except mysql.connector.Error as err:
            print(f"Error al agregar producto: {err}")
            messagebox.showerror("Error de Base de Datos", f"Error al guardar producto: {err}")
            return False

    def actualizar_stock_producto(self, id_producto, nuevo_stock):
        if not self.cursor:
            print("No hay cursor de base de datos.")
            messagebox.showerror("Error de Base de Datos", "No hay conexión activa para actualizar el stock.")
            return False
        
        query = "UPDATE productos SET stock = %s WHERE id = %s"
        try:
            self.cursor.execute(query, (nuevo_stock, id_producto))
            self.connection.commit()
            if self.cursor.rowcount == 0:
                print(f"Advertencia: No se encontró el producto con ID {id_producto} para actualizar stock.")
            print(f"Stock del producto ID {id_producto} actualizado a {nuevo_stock}.")
            return True
        except mysql.connector.Error as err:
            print(f"Error al actualizar stock: {err}")
            messagebox.showerror("Error de Base de Datos", f"Error al actualizar stock: {err}")
            return False

    def obtener_marcas(self):
        if not self.cursor:
            return ["Todas"]
    
        query = "SELECT DISTINCT marca FROM productos WHERE marca IS NOT NULL AND marca != '' AND stock > 0 ORDER BY marca"
        try:
            self.cursor.execute(query)
            marcas = [row['marca'] for row in self.cursor.fetchall()]
            return ["Todas"] + marcas
        except mysql.connector.Error as err:
            print(f"Error al obtener marcas: {err}")
            return ["Todas"]
        
    def actualizar_producto(self, producto):
        if not self.cursor:
            print("No hay cursor de base de datos.")
            messagebox.showerror("Error de Base de Datos", "No hay conexión activa para actualizar el producto.")
            return False
        
        query = """
        UPDATE productos 
        SET nombre = %s, 
            marca = %s, 
            descripcion = %s, 
            precio = %s, 
            stock = %s 
        WHERE id = %s
        """
        values = (
            producto.nombre, 
            producto.marca, 
            producto.descripcion, 
            producto.precio, 
            producto.stock, 
            producto.id_producto  # Ensure 'id_producto' holds the correct ID
        )
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            if self.cursor.rowcount == 0:
                # This means no rows were updated, possibly the ID didn't exist.
                # You might want to log this or handle it more specifically.
                print(f"Advertencia: No se encontró el producto con ID {producto.id_producto} para actualizar, o los datos eran los mismos.")
            else:
                print(f"Producto ID {producto.id_producto} actualizado en la base de datos.")
            return True # Return True even if rowcount is 0, as the command executed.
                        # Or, return self.cursor.rowcount > 0 if you want to be stricter.
        except mysql.connector.Error as err:
            print(f"Error al actualizar producto: {err}")
            messagebox.showerror("Error de Base de Datos", f"Error al actualizar producto: {err}")
            return False

    def cerrar_conexion(self):
        try:
            if self.connection and self.connection.is_connected():
                if self.cursor:
                    self.cursor.close()
                self.connection.close()
                print("Conexión a MySQL cerrada.")
        except mysql.connector.Error as err:
            print(f"Error al cerrar la conexión MySQL: {err}")
        finally:
            self.cursor = None
            self.connection = None
