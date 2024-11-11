import os
from dotenv import load_dotenv
from astrapy import DataAPIClient
from astrapy.operations import InsertMany, ReplaceOne, InsertOne
from astrapy.results import BulkWriteResult


# Cargar variables de entorno
load_dotenv()

astra_database_id=os.getenv("ASTRA_DB_ID")
astra_database_region=os.getenv("ASTRA_DB_REGION")
astra_application_token=os.getenv("ASTRA_DB_APPLICATION_TOKEN")
astra_db_url=os.getenv("ASTRA_DB_BASE_URL")

# Initialize the client
client = DataAPIClient(astra_application_token)
db = client.get_database_by_api_endpoint(astra_db_url)
my_astra_db_admin = client.get_admin()


def check_if_db_active(db_id: str) -> bool:
 db_info = my_astra_db_admin.async_database_info(db_id)
 return db_info.status == "ACTIVE"

# my_collection = db.get_collection('emotion_data');
# op1 = InsertMany([{"a": 1}, {"a": 2}])
# op2 = ReplaceOne({"z": 9}, replacement={"z": 9, "replaced": True}, upsert=True)

# my_collection.bulk_write([op1,op2])
# BulkWriteResult(bulk_api_results={0: ..., 1: ...}, deleted_count=0, inserted_count=3, matched_count=0, modified_count=0, upserted_count=1, upserted_ids={1: '2addd676-...'})
# my_collection.count_documents({}, upper_bound=100)
# my_collection.distinct("replaced");
# print(f"Connected to Astra DB: {db.get_collection('emotion_data')}")

def insert_emotion_data(data):
    """
    Inserta un documento con los datos de emociones en la colección 'emotion_data'.
    """
    try:
        collection = db.get_collection("emotion_data")

        # Crear operación de inserción
        op = InsertOne(data)
        
        # Ejecutar la operación
        result = collection.bulk_write([op])
        print("Documento de emociones insertado exitosamente.")
        
    except Exception as e:
        print(f"Error al insertar el documento de emociones: {e}")