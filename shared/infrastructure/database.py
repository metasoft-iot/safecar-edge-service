"""
Database initialization for the SafeCar Edge Service

This module sets up the database connection and initializes the database schema.
Sets up the SQLite database and creates required tables for devices and sensor readings.
"""

from peewee import SqliteDatabase

# Initialize the SQLite database
db = SqliteDatabase('safecar_edge.db')


def init_db() -> None:
    """
    Initialize the database and create tables for all models.
    """
    # Check if database is already connected
    if not db.is_closed():
        db.close()
    
    db.connect()
    
    # Import models
    from iam.infrastructure.models import Device
    from telemetry.infrastructure.models import SensorReading
    
    # Create tables
    db.create_tables([Device, SensorReading], safe=True)
    
    db.close()
    
    print("Database initialized successfully")
