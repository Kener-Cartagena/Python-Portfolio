# © 2025 Kener Cartagena. Todos los derechos reservados.
# Uso personal únicamente. Prohibida su distribución sin permiso.

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from db import Producto

class App(ctk.CTk):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager

        self.title("PhoneParts Pro - Gestor de Ventas (MySQL)")
        self.geometry("1000x700") 

        self.productos_mostrados = []
        self.producto_seleccionado = None

        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=2) 
        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=0) 
        self.grid_rowconfigure(2, weight=1) 
        self.grid_rowconfigure(3, weight=0) 

        self.lbl_titulo = ctk.CTkLabel(self, text="PPP", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_titulo.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="n")

        self.frame_busqueda = ctk.CTkFrame(self)
        self.frame_busqueda.grid(row=1, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        self.frame_busqueda.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frame_busqueda, text="Buscar por Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_buscar_nombre = ctk.CTkEntry(self.frame_busqueda, placeholder_text="Ej: Pantalla iPhone")
        self.entry_buscar_nombre.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.btn_clear_busqueda = ctk.CTkButton(self.frame_busqueda, text="❌", width=30, command=self.limpiar_busqueda)
        self.btn_clear_busqueda.grid(row=0, column=1, sticky="e", padx=(0, 5))
        
        ctk.CTkLabel(self.frame_busqueda, text="Filtrar por Marca:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.marcas_disponibles = ["Todas"] 
        self.combo_buscar_marca = ctk.CTkComboBox(self.frame_busqueda, values=self.marcas_disponibles)
        self.combo_buscar_marca.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.combo_buscar_marca.set("Todas")

        self.btn_buscar = ctk.CTkButton(self.frame_busqueda, text="Buscar", command=self.buscar_productos)
        self.btn_buscar.grid(row=0, column=4, padx=10, pady=5)

        self.main_content_frame = ctk.CTkFrame(self)
        self.main_content_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.main_content_frame.grid_columnconfigure(0, weight=1) 
        self.main_content_frame.grid_columnconfigure(1, weight=1) 
        self.main_content_frame.grid_rowconfigure(0, weight=1)

        self.frame_lista_productos = ctk.CTkFrame(self.main_content_frame)
        self.frame_lista_productos.grid(row=0, column=0, padx=(0,5), pady=0, sticky="nsew")
        
        ctk.CTkLabel(self.frame_lista_productos, text="Productos Disponibles", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.scrollable_frame_productos = ctk.CTkScrollableFrame(self.frame_lista_productos, height=400) # Puedes ajustar la altura
        self.scrollable_frame_productos.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Frame Contenedor Derecha con Tabs ---
        self.frame_derecha_contenedor = ctk.CTkFrame(self.main_content_frame, fg_color="transparent")
        self.frame_derecha_contenedor.grid(row=0, column=1, padx=(5,0), pady=0, sticky="nsew")
        self.frame_derecha_contenedor.grid_rowconfigure(0, weight=1)
        self.frame_derecha_contenedor.grid_columnconfigure(0, weight=1)

        self.tab_view_derecha = ctk.CTkTabview(self.frame_derecha_contenedor)
        self.tab_view_derecha.grid(row=0, column=0, sticky="nsew")
        self.tab_view_derecha.add("Detalles del Producto") 
        self.tab_view_derecha.add("Añadir Producto")

        # --- Contenido de la Pestaña "Detalles del Producto" ---
        tab_detalles = self.tab_view_derecha.tab("Detalles del Producto")
        # Usamos un frame interno para facilitar el layout con pack para los detalles
        self.frame_detalles_producto_tab_content = ctk.CTkFrame(tab_detalles, fg_color="transparent")
        self.frame_detalles_producto_tab_content.pack(expand=True, fill="both", padx=5, pady=5)

        ctk.CTkLabel(self.frame_detalles_producto_tab_content, text="Información del Producto", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10,15))
        
        self.lbl_detalle_nombre = ctk.CTkLabel(self.frame_detalles_producto_tab_content, text="Nombre: -", wraplength=380, justify="left") # Ajustar wraplength si es necesario
        self.lbl_detalle_nombre.pack(pady=4, anchor="w", padx=10)
        self.lbl_detalle_marca = ctk.CTkLabel(self.frame_detalles_producto_tab_content, text="Marca: -")
        self.lbl_detalle_marca.pack(pady=4, anchor="w", padx=10)
        self.lbl_detalle_descripcion = ctk.CTkLabel(self.frame_detalles_producto_tab_content, text="Descripción: -", wraplength=380, justify="left")
        self.lbl_detalle_descripcion.pack(pady=4, anchor="w", padx=10)
        self.lbl_detalle_precio = ctk.CTkLabel(self.frame_detalles_producto_tab_content, text="Precio: -")
        self.lbl_detalle_precio.pack(pady=4, anchor="w", padx=10)
        self.lbl_detalle_stock = ctk.CTkLabel(self.frame_detalles_producto_tab_content, text="Stock: -", font=ctk.CTkFont(weight="bold"))
        self.lbl_detalle_stock.pack(pady=4, anchor="w", padx=10)

        # Frame para agrupar entry y botón de vender
        frame_vender_controles = ctk.CTkFrame(self.frame_detalles_producto_tab_content, fg_color="transparent")
        frame_vender_controles.pack(pady=(15,10), padx=10, fill="x")
        self.entry_cantidad_vender = ctk.CTkEntry(frame_vender_controles, placeholder_text="Cant.", width=70)
        self.entry_cantidad_vender.pack(side="left", padx=(0,10))
        self.btn_vender = ctk.CTkButton(frame_vender_controles, text="Vender Producto", command=self.vender_producto, state="disabled")
        self.btn_vender.pack(side="left", expand=True, fill="x")

        self.frame_formulario_actualizacion = ctk.CTkScrollableFrame(
            self.frame_detalles_producto_tab_content,
            fg_color="transparent",
            height=250  # Ajusta según cuánto espacio quieras permitir antes de mostrar scroll
        )

        # Campos editables
        self.entry_edit_nombre = ctk.CTkEntry(self.frame_formulario_actualizacion, placeholder_text="Nombre")
        self.entry_edit_nombre.pack(pady=5, fill="x")

        self.entry_edit_marca = ctk.CTkEntry(self.frame_formulario_actualizacion, placeholder_text="Marca")
        self.entry_edit_marca.pack(pady=5, fill="x")

        self.text_edit_descripcion = ctk.CTkTextbox(self.frame_formulario_actualizacion, height=80)
        self.text_edit_descripcion.pack(pady=5, fill="x")

        self.entry_edit_precio = ctk.CTkEntry(self.frame_formulario_actualizacion, placeholder_text="Precio")
        self.entry_edit_precio.pack(pady=5, fill="x")

        self.entry_edit_stock = ctk.CTkEntry(self.frame_formulario_actualizacion, placeholder_text="Cantidad a añadir") #
        self.entry_edit_stock.pack(pady=5, fill="x")

        self.btn_guardar_cambios = ctk.CTkButton(self.frame_formulario_actualizacion, text="Guardar Cambios", command=self.guardar_cambios_producto)
        self.btn_guardar_cambios.pack(pady=10)


        self.btn_actualizar_producto = ctk.CTkButton(
            frame_vender_controles,
            text="Actualizar Producto",
            command=self.mostrar_formulario_actualizacion
        )
        self.btn_actualizar_producto.pack(side="left", padx=(10, 0), fill="x", expand=True)


        # --- Contenido de la Pestaña "Añadir Producto" ---
        tab_anadir = self.tab_view_derecha.tab("Añadir Producto")
        # Usamos un frame interno que usará grid para el formulario
        self.frame_anadir_producto_tab_content = ctk.CTkFrame(tab_anadir, fg_color="transparent")
        self.frame_anadir_producto_tab_content.pack(expand=True, fill="both", padx=5, pady=5)
        self.frame_anadir_producto_tab_content.grid_columnconfigure(1, weight=1) # Columna de entries se expande

        ctk.CTkLabel(self.frame_anadir_producto_tab_content, text="Registrar Nuevo Producto", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(10,15), padx=5)

        ctk.CTkLabel(self.frame_anadir_producto_tab_content, text="Nombre:").grid(row=1, column=0, padx=5, pady=7, sticky="w")
        self.entry_add_nombre = ctk.CTkEntry(self.frame_anadir_producto_tab_content, placeholder_text="Nombre del producto")
        self.entry_add_nombre.grid(row=1, column=1, padx=5, pady=7, sticky="ew")

        ctk.CTkLabel(self.frame_anadir_producto_tab_content, text="Marca:").grid(row=2, column=0, padx=5, pady=7, sticky="w")
        self.entry_add_marca = ctk.CTkEntry(self.frame_anadir_producto_tab_content, placeholder_text="Marca del producto")
        self.entry_add_marca.grid(row=2, column=1, padx=5, pady=7, sticky="ew")

        ctk.CTkLabel(self.frame_anadir_producto_tab_content, text="Descripción:").grid(row=3, column=0, padx=5, pady=7, sticky="nw") # sticky nw para alinear con textbox
        self.entry_add_descripcion = ctk.CTkTextbox(self.frame_anadir_producto_tab_content, height=80)
        self.entry_add_descripcion.grid(row=3, column=1, padx=5, pady=7, sticky="ew")

        ctk.CTkLabel(self.frame_anadir_producto_tab_content, text="Precio (HNL):").grid(row=4, column=0, padx=5, pady=7, sticky="w")
        self.entry_add_precio = ctk.CTkEntry(self.frame_anadir_producto_tab_content, placeholder_text="0.00")
        self.entry_add_precio.grid(row=4, column=1, padx=5, pady=7, sticky="ew")

        ctk.CTkLabel(self.frame_anadir_producto_tab_content, text="Stock Inicial:").grid(row=5, column=0, padx=5, pady=7, sticky="w")
        self.entry_add_stock = ctk.CTkEntry(self.frame_anadir_producto_tab_content, placeholder_text="0")
        self.entry_add_stock.grid(row=5, column=1, padx=5, pady=7, sticky="ew")

        self.btn_add_producto = ctk.CTkButton(self.frame_anadir_producto_tab_content, text="Guardar Nuevo Producto", command=self.anadir_producto, height=35)
        self.btn_add_producto.grid(row=6, column=0, columnspan=2, padx=10, pady=(20,10)) # Más pady superior
        
        # --- Status Bar ---
        self.lbl_status = ctk.CTkLabel(self, text="Conectando a la base de datos...", anchor="w")
        self.lbl_status.grid(row=3, column=0, columnspan=2, padx=20, pady=(5,10), sticky="ew")

        # --- Cargar datos iniciales ---
        if self.db_manager.conectar():
            self.lbl_status.configure(text="Conectado a la base de datos. Listo.")
            self.actualizar_lista_productos()
            self.actualizar_combo_marcas()
        else:
            self.lbl_status.configure(text="Error: No se pudo conectar a la base de datos. Revise la consola.")
            self.btn_buscar.configure(state="disabled")
            # No podemos configurar btn_add_producto aquí porque aún no se ha creado en su tab
            # Se podría deshabilitar el tab o los campos dentro de él si la conexión falla.
            # Por ahora, el mensaje de error es la principal indicación.

    def actualizar_lista_productos(self, nombre_buscar=None, marca_buscar=None):
        """Limpia y recarga la lista de productos en la GUI."""
        for widget in self.scrollable_frame_productos.winfo_children():
            widget.destroy()
        
        self.productos_mostrados = self.db_manager.obtener_productos(nombre_buscar, marca_buscar)
        
        if not self.productos_mostrados:
            ctk.CTkLabel(self.scrollable_frame_productos, text="No se encontraron productos.").pack(pady=10)
            self.limpiar_detalles_producto() 
            return

        for i, producto in enumerate(self.productos_mostrados):
            texto_producto = f"{producto.nombre} ({producto.marca}) - Stock: {producto.stock}"
            btn = ctk.CTkButton(self.scrollable_frame_productos, text=texto_producto,
                                command=lambda p=producto: self.seleccionar_producto(p))
            btn.pack(fill="x", pady=2, padx=5)
        
        self.limpiar_detalles_producto()

    def buscar_productos(self):
        """Obtiene los filtros y actualiza la lista de productos."""
        nombre = self.entry_buscar_nombre.get()
        marca = self.combo_buscar_marca.get()
        self.actualizar_lista_productos(nombre, marca)
        self.lbl_status.configure(text=f"Búsqueda realizada. {len(self.productos_mostrados)} productos encontrados.")

    def limpiar_busqueda(self):
        self.entry_buscar_nombre.delete(0, tk.END)
        self.combo_buscar_marca.set("Todas")
        self.actualizar_lista_productos()
        self.lbl_status.configure(text="Filtro limpiado. Mostrando todos los productos.")


    def seleccionar_producto(self, producto):
        """Muestra los detalles del producto seleccionado y habilita el botón de vender."""
        self.producto_seleccionado = producto
        self.lbl_detalle_nombre.configure(text=f"Nombre: {producto.nombre}")
        self.lbl_detalle_marca.configure(text=f"Marca: {producto.marca}")
        self.lbl_detalle_descripcion.configure(text=f"Descripción: {producto.descripcion}")
        self.lbl_detalle_precio.configure(text=f"Precio: ${float(producto.precio):.2f}")
        self.lbl_detalle_stock.configure(text=f"Stock: {producto.stock}")
        self.btn_vender.configure(state="normal" if producto.stock > 0 else "disabled")
        self.entry_cantidad_vender.delete(0, tk.END)
        self.entry_cantidad_vender.insert(0, "1") 
        self.lbl_status.configure(text=f"Producto seleccionado: {producto.nombre}")
        self.tab_view_derecha.set("Detalles del Producto") # Cambiar a la pestaña de detalles

    def limpiar_detalles_producto(self):
        """Limpia el panel de detalles del producto."""
        self.producto_seleccionado = None
        self.lbl_detalle_nombre.configure(text="Nombre: -")
        self.lbl_detalle_marca.configure(text="Marca: -")
        self.lbl_detalle_descripcion.configure(text="Descripción: -")
        self.lbl_detalle_precio.configure(text="Precio: -")
        self.lbl_detalle_stock.configure(text="Stock: -")
        self.btn_vender.configure(state="disabled")
        self.entry_cantidad_vender.delete(0, tk.END)

    def vender_producto(self):
        """Maneja la lógica de venta de un producto."""
        if not self.producto_seleccionado:
            messagebox.showwarning("Venta Inválida", "Por favor, seleccione un producto primero.")
            return

        try:
            cantidad_a_vender = int(self.entry_cantidad_vender.get())
            if cantidad_a_vender <= 0:
                messagebox.showerror("Error de Cantidad", "La cantidad a vender debe ser mayor que cero.")
                return
            if cantidad_a_vender > self.producto_seleccionado.stock:
                messagebox.showerror("Stock Insuficiente", 
                                     f"No hay suficiente stock. Disponible: {self.producto_seleccionado.stock}")
                return
        except ValueError:
            messagebox.showerror("Error de Entrada", "La cantidad a vender debe ser un número entero.")
            return

        nuevo_stock = self.producto_seleccionado.stock - cantidad_a_vender
        if self.db_manager.actualizar_stock_producto(self.producto_seleccionado.id_producto, nuevo_stock):
            self.lbl_status.configure(text=f"¡Venta exitosa! {cantidad_a_vender} unidad(es) de '{self.producto_seleccionado.nombre}' vendida(s).")
            id_producto_vendido = self.producto_seleccionado.id_producto
            self.actualizar_lista_productos(self.entry_buscar_nombre.get(), self.combo_buscar_marca.get()) 
            self.actualizar_combo_marcas()

            producto_actualizado = next((p for p in self.productos_mostrados if p.id_producto == id_producto_vendido), None)
            if producto_actualizado:
                self.seleccionar_producto(producto_actualizado) # Esto también cambiará a la pestaña de detalles
            else: 
                self.limpiar_detalles_producto()
        else:
            self.lbl_status.configure(text="Error al procesar la venta.")
            
    def anadir_producto(self):
        """Maneja la lógica para añadir un nuevo producto."""
        nombre = self.entry_add_nombre.get()
        marca = self.entry_add_marca.get()
        descripcion = self.entry_add_descripcion.get("1.0", tk.END).strip()
        
        try:
            precio_str = self.entry_add_precio.get()
            stock_str = self.entry_add_stock.get()

            if not precio_str or not stock_str:
                 messagebox.showerror("Error de Entrada", "Precio y Stock no pueden estar vacíos.")
                 return

            precio = float(precio_str)
            stock = int(stock_str)
            
            if precio < 0 or stock < 0:
                messagebox.showerror("Error de Entrada", "Precio y stock no pueden ser negativos.")
                return
        except ValueError:
            messagebox.showerror("Error de Entrada", "Precio debe ser un número (ej: 120.50) y Stock un número entero.")
            self.lbl_status.configure(text="Error: Datos inválidos para nuevo producto.")
            return

        if not nombre:
            messagebox.showerror("Error de Entrada", "El nombre del producto es obligatorio.")
            self.lbl_status.configure(text="Error: El nombre del producto es obligatorio.")
            return

        nuevo_producto = Producto(None, nombre, marca, descripcion, precio, stock) 
        
        if self.db_manager.agregar_producto(nuevo_producto):
            self.lbl_status.configure(text=f"Producto '{nombre}' añadido exitosamente.")
            self.actualizar_lista_productos() 
            self.actualizar_combo_marcas() 
            self.entry_add_nombre.delete(0, tk.END)
            self.entry_add_marca.delete(0, tk.END)
            self.entry_add_descripcion.delete("1.0", tk.END)
            self.entry_add_precio.delete(0, tk.END)
            self.entry_add_stock.delete(0, tk.END)
            messagebox.showinfo("Producto Añadido", f"El producto '{nombre}' ha sido guardado exitosamente.")
        else:
            self.lbl_status.configure(text="Error al añadir el producto.")

    def actualizar_combo_marcas(self):
        """Actualiza las opciones del ComboBox de marcas."""
        marcas_actuales = self.db_manager.obtener_marcas()
        # Solo reconfigurar si hay un cambio real para evitar flickering o resets innecesarios
        if self.combo_buscar_marca.cget("values") != marcas_actuales:
            current_selection = self.combo_buscar_marca.get()
            self.marcas_disponibles = marcas_actuales
            self.combo_buscar_marca.configure(values=self.marcas_disponibles)
            if current_selection in self.marcas_disponibles:
                self.combo_buscar_marca.set(current_selection)
            else:
                self.combo_buscar_marca.set("Todas")

    def mostrar_formulario_actualizacion(self):
        if not self.producto_seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un producto primero.")
            return

        # Llenar campos con datos actuales
        p = self.producto_seleccionado
        self.entry_edit_nombre.delete(0, tk.END)
        self.entry_edit_nombre.insert(0, p.nombre)

        self.entry_edit_marca.delete(0, tk.END)
        self.entry_edit_marca.insert(0, p.marca)

        self.text_edit_descripcion.delete("1.0", tk.END)
        self.text_edit_descripcion.insert("1.0", p.descripcion)

        self.entry_edit_precio.delete(0, tk.END)
        self.entry_edit_precio.insert(0, str(p.precio))

        self.entry_edit_stock.delete(0, tk.END)

        # Mostrar formulario
        self.frame_formulario_actualizacion.pack(fill="both", expand=False, padx=10, pady=(10, 5))


    def guardar_cambios_producto(self):
        if not self.producto_seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un producto primero.")
            return

        # Obtener el producto original para acceder a su stock actual
        producto_original = self.producto_seleccionado #

        try:
            nuevo_nombre = self.entry_edit_nombre.get().strip()
            nueva_marca = self.entry_edit_marca.get().strip()
            nueva_descripcion = self.text_edit_descripcion.get("1.0", tk.END).strip() #

            precio_str = self.entry_edit_precio.get()
            if not precio_str:
                messagebox.showerror("Error de Entrada", "El Precio no puede estar vacío.")
                return
            nuevo_precio = float(precio_str) #

            cantidad_a_anadir_str = self.entry_edit_stock.get() #
            if not cantidad_a_anadir_str: # Si el campo está vacío, se asume que no se añade ni se quita stock
                cantidad_a_anadir = 0
            else:
                cantidad_a_anadir = int(cantidad_a_anadir_str) # Puede generar ValueError

            # Calcular el nuevo stock final
            nuevo_stock_final = producto_original.stock + cantidad_a_anadir #

            if not nuevo_nombre:
                messagebox.showerror("Error", "El nombre no puede estar vacío.") #
                return
            if nuevo_precio < 0:
                messagebox.showerror("Error", "El precio no puede ser negativo.") #
                return
            if nuevo_stock_final < 0: # Validar que el stock resultante no sea negativo
                messagebox.showerror("Error", "El stock resultante no puede ser negativo.") #
                return
        except ValueError:
            messagebox.showerror("Error", "Precio debe ser un número y la cantidad a añadir al stock debe ser un número entero.") #
            return

        # Actualizar los datos del objeto producto_original (que es self.producto_seleccionado)
        producto_original.nombre = nuevo_nombre #
        producto_original.marca = nueva_marca #
        producto_original.descripcion = nueva_descripcion #
        producto_original.precio = nuevo_precio #
        producto_original.stock = nuevo_stock_final # Usar el stock final calculado

        if self.db_manager.actualizar_producto(producto_original): #
            self.lbl_status.configure(text=f"Producto '{producto_original.nombre}' actualizado correctamente.") #
            messagebox.showinfo("Éxito", f"'{producto_original.nombre}' actualizado.") #

            # Refrescar la lista y los combos
            self.actualizar_lista_productos(self.entry_buscar_nombre.get(), self.combo_buscar_marca.get()) #
            self.actualizar_combo_marcas() #

            # Seleccionar nuevamente para actualizar detalles
            producto_actualizado_en_lista = next((prod for prod in self.productos_mostrados if prod.id_producto == producto_original.id_producto), None) #
            if producto_actualizado_en_lista:
                self.seleccionar_producto(producto_actualizado_en_lista) #
            else:
                # Esto podría pasar si el stock se actualiza a 0 y la lista principal los oculta
                self.limpiar_detalles_producto() #

            # Ocultar el formulario
            self.frame_formulario_actualizacion.pack_forget() #
        else:
            self.lbl_status.configure(text="Error al actualizar el producto.") #


    def on_closing(self):
        """Maneja el cierre de la aplicación."""
        if messagebox.askokcancel("Salir", "¿Está seguro que desea salir de PhoneParts Pro?"):
            self.db_manager.cerrar_conexion()
            self.destroy()
            