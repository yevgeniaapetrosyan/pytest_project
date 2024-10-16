import pytest
import pymssql

# Database connection parameters
DB_HOST = 'localhost'
DB_PORT = 1433
DB_USER = 'user_robot'
DB_PASSWORD = 'robot_pass123'
DB_NAME = 'AdventureWorksDW2012'


@pytest.fixture(scope='module')
def db_connection():
    connection = pymssql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    return connection


def test_table_exists(db_connection):
    """Verify if table dbo.DimCustomer was loaded to database and contains data."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM dbo.dimCustomer")
    output = cursor.fetchone()
    assert output[0] > 0, "Table dbo.DimCustomer is empty or does not exist."


def test_column_not_nullable(db_connection):
    """Verify if table dbo.DimCustomer column geographyKey doesn't contain null values."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM dbo.dimCustomer WHERE geographyKey IS NULL")
    output = cursor.fetchone()
    assert output[0] == 0, "Column geographyKey contains null values."


def test_data_validity_safety_stock_level(db_connection):
    """Verify if table dbo.DimProduct column SafetyStockLevel contains values from allowed range."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM dbo.DimProduct WHERE SafetyStockLevel NOT BETWEEN 0 AND 1000")
    output = cursor.fetchall()
    assert len(output) == 0, "SafetyStockLevel contains invalid values."


def test_future_date_existence(db_connection):
    """Verify if table dbo.DimProduct column startDate doesn't contain future values."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM dbo.DimProduct WHERE startDate > GETDATE()")
    output = cursor.fetchone()
    assert output[0] == 0, "Column startDate contains future values."


def test_record_duplicates(db_connection):
    """Verify if table dbo.FactProductInventory PK columns do not contain duplicates."""
    cursor = db_connection.cursor()
    cursor.execute("""
        SELECT productKey, dateKey, COUNT(*) AS cnt 
        FROM dbo.FactProductInventory 
        GROUP BY productKey, dateKey 
        HAVING COUNT(*) > 1
    """)
    output = cursor.fetchall()
    assert len(output) == 0, "There are duplicate records in PK."


def test_no_negative_values(db_connection):
    """Verify if table dbo.FactProductInventory unitsIn, unitsOut columns do not contain negative values."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM dbo.FactProductInventory WHERE unitsIn < 0 OR unitsOut < 0")
    output = cursor.fetchall()
    assert len(output) == 0, "There are negative values in unitsIn or unitsOut."

