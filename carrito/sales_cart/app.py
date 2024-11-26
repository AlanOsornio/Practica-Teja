from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Función para obtener la conexión a la base de datos
def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

# Ruta principal para ver los productos
@app.route('/')
def index():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener todos los productos de la base de datos
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('index.html', products=products)

# Ruta para agregar productos al carrito
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = request.form.get('quantity', 1, type=int)

    connection = get_db_connection()
    cursor = connection.cursor()

    # Verificar si el producto ya está en el carrito
    cursor.execute("SELECT id, quantity FROM cart WHERE product_id = %s", (product_id,))
    cart_item = cursor.fetchone()
    cursor.fetchall()  # Asegurarse de limpiar resultados pendientes

    if cart_item:
        new_quantity = cart_item[1] + quantity
        cursor.execute("UPDATE cart SET quantity = %s WHERE id = %s", (new_quantity, cart_item[0]))
    else:
        cursor.execute("INSERT INTO cart (product_id, quantity) VALUES (%s, %s)", (product_id, quantity))

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('cart'))

# Ruta para ver el carrito
@app.route('/cart')
def cart():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener los productos del carrito
    cursor.execute("""
        SELECT p.name, p.price, c.quantity, c.id
        FROM cart c
        JOIN products p ON c.product_id = p.id
    """)
    cart_items = cursor.fetchall()

    total = sum(item[1] * item[2] for item in cart_items)

    cursor.close()
    connection.close()

    return render_template('cart.html', cart_items=cart_items, total=total)

# Ruta para eliminar productos del carrito
@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Eliminar el producto del carrito
    cursor.execute("DELETE FROM cart WHERE id = %s", (item_id,))
    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for('cart'))

# Ruta para realizar el checkout y crear la orden
@app.route('/checkout', methods=['POST'])
def checkout():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener todos los productos del carrito
    cursor.execute("""
        SELECT c.product_id, p.price, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.id
    """)
    cart_items = cursor.fetchall()

    # Calcular el total
    total_amount = sum(item[1] * item[2] for item in cart_items)

    # Crear la nueva orden
    cursor.execute("INSERT INTO orders (total_amount) VALUES (%s)", (total_amount,))
    order_id = cursor.lastrowid

    # Crear los detalles de la orden
    for item in cart_items:
        cursor.execute("""
            INSERT INTO order_details (order_id, product_id, quantity, price)
            VALUES (%s, %s, %s, %s)
        """, (order_id, item[0], item[2], item[1]))

    # Vaciar el carrito
    cursor.execute("DELETE FROM cart")
    
    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('order_confirmation', order_id=order_id))

# Ruta de confirmación de la orden
@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, total_amount FROM orders WHERE id = %s", (order_id,))
    order = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template('checkout.html', order=order)

if __name__ == '__main__':
    app.run(debug=True)
