import config
from sqlalchemy import create_engine, text

connection_string = config.get_connection_string()



print("Connection string built successfully.")

engine = create_engine(connection_string)

with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM appointments"))
    count = result.scalar()
    print(f"Connected! Row count in appointments table: {count}")