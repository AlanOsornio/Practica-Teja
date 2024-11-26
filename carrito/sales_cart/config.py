import mysql.connector  # Correcto: usamos el paquete mysql.connector
import os  # Necesario para usar os.urandom

class Config:
    SECRET_KEY = os.urandom(24)  # Para las sesiones y formularios
    SESSION_TYPE = 'filesystem'  # Tipo de sesión (puedes usar Redis, pero en este caso usamos archivo)
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''  # Deja en blanco si no tienes contraseña
    MYSQL_DB = 'sales_cart'  # Nombre de tu base de datos
