import os
import urllib 

DB_SERVER = os.getenv("DB_SERVER", "DESKTOP-G8LSL7V\\SQLEXPRESS")
DB_DATABASE= os.getenv("DB_DATABASE", "sofyrus")
DB_DRIVER = "ODBC Driver 18 for SQL Server"

def get_connection_string():
    params = urllib.parse.quote_plus(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=DESKTOP-G8LSL7V\\SQLEXPRESS;"
        "DATABASE=sofyrus;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    return f"mssql+pyodbc:///?odbc_connect={params}"
