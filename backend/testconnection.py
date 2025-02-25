import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sirajul12@",
        database="ticket_genius"
    )

    if connection.is_connected():
        print("Connection successful!")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("Connection closed.")
