from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Función para obtener la conexión a la base de datos
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # Si no tienes contraseña, déjalo vacío
        database='sales_cart'
    )

# Ruta para mostrar todos los productos
@app.route('/')
def show_products():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Trabajar con resultados como diccionario
    cursor.execute("SELECT * FROM products;")  # Consulta para obtener todos los productos
    products = cursor.fetchall()  # Obtener todos los productos
    cursor.close()
    connection.close()
    return render_template('products.html', products=products)

# Ruta para agregar un producto
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        
        # Insertar el nuevo producto en la base de datos
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s)", (name, price))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('show_products'))  # Redirige a la lista de productos

    return render_template('add_product.html')

# Ruta para editar un producto
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
    product = cursor.fetchone()
    
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        
        # Actualizar el producto en la base de datos
        cursor.execute("UPDATE products SET name = %s, price = %s WHERE id = %s", (name, price, id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('show_products'))  # Redirige a la lista de productos

    cursor.close()
    connection.close()
    return render_template('edit_product.html', product=product)

# Ruta para eliminar un producto
@app.route('/delete/<int:id>', methods=['POST'])
def delete_product(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (id,))
    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('show_products'))  # Redirige a la lista de productos

if __name__ == '__main__':
    app.run(debug=True)
