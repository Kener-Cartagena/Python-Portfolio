import tkinter as tk
from tkinter import ttk, messagebox
from base_datos import obtener_conexion

class InventarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Inventario - Seminario Menor Santiago Apóstol")
        self.root.config(bg="#FAEBD7")
        self.root.geometry("800x600")
        
        # Crear conexión a la base de datos
        self.conn = obtener_conexion()
        self.cursor = self.conn.cursor()

        self.crear_interfaz()

    def crear_interfaz(self):
        tk.Label(self.root, text="Categoría", bg="#FAEBD7", fg="#000000", font=("Cascadia Code Semibold", 14)).grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Descripción", bg="#FAEBD7", fg="#000000", font=("Cascadia Code Semibold", 14)).grid(row=1, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Cantidad", bg="#FAEBD7", fg="#000000", font=("Cascadia Code Semibold", 14)).grid(row=2, column=0, padx=10, pady=10)
        
        self.categoria_var = tk.StringVar()
        self.descripcion_var = tk.StringVar()
        self.cantidad_var = tk.IntVar()
        
        categorias = ["Cocina", "Comedor", "Lavandería", "Capilla", "Biblioteca y sala de estudio",
                      "Centro vocacional", "Oficinas", "Pabellones", "Cuarto de seminaristas",
                      "Habitaciones de formadores", "Habitaciones de huéspedes", "Artículos navideños",
                      "Hotelitos", "Mobiliarios varios"]
        
        self.categoria_combobox = ttk.Combobox(self.root, textvariable=self.categoria_var, font=("Cascadia Code Semibold", 10), values=categorias, state="readonly")
        self.categoria_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        tk.Entry(self.root, textvariable=self.descripcion_var, font=("Cascadia Code Semibold", 10)).grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        tk.Entry(self.root, textvariable=self.cantidad_var, font=("Cascadia Code Semibold", 10)).grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        tk.Button(self.root, text="Agregar", bg="#2F4F4F", fg="#E6E6FA", font=("Cascadia Code Semibold", 10), command=self.agregar_item).grid(row=3, column=0, padx=10, pady=20)
        tk.Button(self.root, text="Mostrar Inventario", bg="#2F4F4F", fg="#E6E6FA", font=("Cascadia Code Semibold", 10), command=self.mostrar_inventario).grid(row=3, column=1, padx=10, pady=20)
        tk.Button(self.root, text="Eliminar", bg="#2F4F4F", fg="#E6E6FA", font=("Cascadia Code Semibold", 10), command=self.eliminar_item).grid(row=4, column=0, padx=10, pady=20)
        tk.Button(self.root, text="Eliminar Todo", bg="red", fg="#FFFFF0", font=("Cascadia Code Semibold", 10), command=self.eliminar_todo).grid(row=4, column=1, padx=10, pady=20)
        tk.Button(self.root, text="Salir", bg="#2F4F4F", fg="#E6E6FA", font=("Cascadia Code Semibold", 10), command=self.salir).grid(row=6, column=1, columnspan=2, padx=10, pady=20)

        self.tree = ttk.Treeview(self.root, columns=("id", "categoria", "descripcion", "cantidad"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("categoria", text="Categoría")
        self.tree.heading("descripcion", text="Descripción")
        self.tree.heading("cantidad", text="Cantidad")
        self.tree.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def agregar_item(self):
        categoria = self.categoria_var.get()
        descripcion = self.descripcion_var.get()
        cantidad = self.cantidad_var.get()

        if not categoria or not descripcion or cantidad <= 0:
            messagebox.showerror("Error", "Todos los campos son obligatorios y la cantidad debe ser mayor a 0.")
            return

        self.cursor.execute("INSERT INTO inventario (categoria, descripcion, cantidad) VALUES (?, ?, ?)", (categoria, descripcion, cantidad))
        self.conn.commit()
        messagebox.showinfo("Éxito", "Elemento agregado correctamente.")
        self.mostrar_inventario()

    def eliminar_item(self):
        if not self.tree.selection():
            messagebox.showerror("Error", "Debe seleccionar un elemento para eliminar.")
            return
        item_seleccionado = self.tree.selection()[0]
        id_seleccionado = self.tree.item(item_seleccionado)["values"][0]
        self.cursor.execute("DELETE FROM inventario WHERE id=?", (id_seleccionado,))
        self.conn.commit()
        messagebox.showinfo("Éxito", "Elemento eliminado correctamente.")
        self.mostrar_inventario()

    def eliminar_todo(self):
        respuesta = messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar todo el inventario?")
        if respuesta:
            self.cursor.execute("DELETE FROM inventario")
            self.conn.commit()
            messagebox.showinfo("Éxito", "Todo el inventario ha sido eliminado.")
            self.mostrar_inventario()

    def mostrar_inventario(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.cursor.execute("SELECT * FROM inventario")
        for fila in self.cursor.fetchall():
            self.tree.insert("", tk.END, values=fila)

    def salir(self):
        respuesta = messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas salir?")
        if respuesta:
            self.conn.close()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = InventarioApp(root)
    root.mainloop()
