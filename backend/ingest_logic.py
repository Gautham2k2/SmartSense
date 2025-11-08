import os
import json
import pandas as pd
import sys
import uuid
import fitz  # this is from the PyMuPDF module
from tqdm import tqdm

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, JSON, TEXT
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.orm import sessionmaker
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
sys.path.append(ROOT_DIR)

try:
    from inference_logic import parse_floorplan
except ImportError:
    print("Error: Could not import 'parse_floorplan' from 'inference_logic'.")
    sys.exit(1)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST") # 'mysql_db'
DB_PORT = os.getenv("DB_PORT") # '3306'
DB_NAME = os.getenv("DB_NAME")

MYSQL_DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DB_TABLE_NAME = "properties"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION = "property_search"
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
EXCEL_PATH = os.path.join(ASSETS_DIR, "Property_list.xlsx")
IMAGE_DIR = os.path.join(ASSETS_DIR, "images")
CERT_DIR = os.path.join(ASSETS_DIR, "certificates")
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
EMBEDDING_DIMENSION = 384
metadata = MetaData()

def get_db_session():
    print(f"Connecting to Local MySQL at {MYSQL_DB_URL.split('@')[-1]}...")
    try:
        engine = create_engine(MYSQL_DB_URL)
        Session = sessionmaker(bind=engine)
        print("Local MySQL connection successful.")
        return engine, Session()
    except Exception as e:
        print(f"Cannot connect to Local MySQL: {e}")
        sys.exit(1)

def setup_mysql_table(engine):
    try:
        properties_table = Table(
            DB_TABLE_NAME,
            metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('property_id', String(255), index=True, unique=True),
            Column('title', String(1024)),
            Column('long_description', TEXT),
            Column('location', String(1024)),
            Column('price', Float),
            Column('seller_type', String(255)),
            Column('listing_date', String(255)),
            Column('certificates', String(1024)),
            Column('seller_contact', String(255)),
            Column('metadata_tags', String(1024)),
            Column('floorplan_data', TEXT) 
        )
        metadata.create_all(engine)
        print(f"MySQL table '{DB_TABLE_NAME}' ensured to exist.")
        return properties_table
    except Exception as e:
        print(f"--- FATAL ERROR --- Error during table setup: {e}")
        sys.exit(1)


def get_qdrant_client_instance():
    print(f"Connecting to Local Qdrant at {QDRANT_HOST}:{QDRANT_PORT}...")
    try:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        if client.collection_exists(collection_name=QDRANT_COLLECTION):
             print(f"Qdrant collection '{QDRANT_COLLECTION}' already exists. Recreating...")
             client.delete_collection(collection_name=QDRANT_COLLECTION)
        
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=models.VectorParams(
                size=EMBEDDING_DIMENSION,
                distance=models.Distance.COSINE
            )
        )
        print(f"Qdrant collection '{QDRANT_COLLECTION}' created.")
        return client
    except Exception as e:
        print(f"Cannot connect to Local Qdrant: {e}")
        sys.exit(1)


def load_embedding_model():
    print(f"Loading embedding model '{EMBEDDING_MODEL_NAME}'...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("Embedding model loaded.")
    return model

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"Could not parse PDF {pdf_path}. Error: {e}")
    return text.strip()


def run_etl():
    print("\n--- Starting: ETL Process ---")

    mysql_engine, db_session = get_db_session()
    qdrant_client = get_qdrant_client_instance()
    embedding_model = load_embedding_model()
    properties_table = setup_mysql_table(mysql_engine)
    
    try:
        df = pd.read_excel(EXCEL_PATH)
    except FileNotFoundError:
        print(f"Fatal Error: Excel file not found at {EXCEL_PATH}")
        return
        
    print(f"Loaded {len(df)} properties from Excel.")

    print("Cleaning data... Replacing NaN with defaults.")
    df['title'] = df['title'].fillna('') 
    df['long_description'] = df['long_description'].fillna('')
    df['certificates'] = df['certificates'].fillna('')
    df['price'] = df['price'].fillna(0.0)
    
    qdrant_points = [] 
    
    print("Processing properties...")
    for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Properties"):
        try:
            prop_id = str(row['property_id'])
            
            image_file_name = row['image_file']
            image_full_path = os.path.join(IMAGE_DIR, image_file_name)
            
            if not os.path.exists(image_full_path):
                floorplan_json_string = json.dumps({"error": "image_file_not_found"})
            else:
                floorplan_json_string = parse_floorplan(image_full_path)

            property_record = {
                'property_id': prop_id,
                'title': row.get('title'),
                'long_description': row.get('long_description'),
                'location': row.get('location'),
                'price': row.get('price'),
                'seller_type': row.get('seller_type'),
                'listing_date': str(row.get('listing_date')),
                'certificates': row.get('certificates'),
                'seller_contact': str(row.get('seller_contact')),
                'metadata_tags': row.get('metadata_tags'),
                'floorplan_data': floorplan_json_string
            }
            
            # --- THIS IS THE FIX ---
            # Create the insert statement
            stmt = mysql_insert(properties_table).values(property_record)

            # Create the 'on duplicate' update dictionary
            # This uses .inserted (for MySQL) instead of .excluded (for Postgres)
            update_on_conflict = {
                c.name: stmt.inserted[c.name]
                for c in properties_table.columns
                if c.name not in ["id", "property_id"] # Don't update keys
            }

            # Apply the on_duplicate_key_update
            stmt = stmt.on_duplicate_key_update(**update_on_conflict)
            # --- END OF FIX ---

            db_session.execute(stmt)

            # ... (rest of the Qdrant and PDF logic is unchanged) ...
            text_chunks = []
            desc_text = f"Title: {row.get('title', '')}. Description: {row.get('long_description', '')}"
            text_chunks.append(desc_text)
            
            pdf_text = ""
            cert_files = str(row.get('certificates', '')).split('|') 
            for cert_file in cert_files:
                cert_file = cert_file.strip()
                if cert_file:
                    cert_full_path = os.path.join(CERT_DIR, cert_file)
                    if os.path.exists(cert_full_path):
                        pdf_text += extract_text_from_pdf(cert_full_path) + " "
            
            if pdf_text:
                text_chunks.append(pdf_text)
            
            embeddings = embedding_model.encode(text_chunks)
            
            for i, (text_chunk, embedding) in enumerate(zip(text_chunks, embeddings)):
                qdrant_points.append(
                    models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding.tolist(),
                        payload={
                            "text": text_chunk,
                            "property_id": prop_id,
                            "chunk_type": "description" if i == 0 else "certificate"
                        }
                    )
                )

        except Exception as e:
            print(f"Error processing property {row.get('property_id')}: {e}")
            db_session.rollback()
            continue
            
    
    try:
        db_session.commit()
        print("Successfully saved all structured data to Local MySQL.")
    except Exception as e:
        print(f"Error committing to MySQL: {e}")
        db_session.rollback()
        
    if qdrant_points:
        print(f"Uploading {len(qdrant_points)} text chunks to Local Qdrant...")
        qdrant_client.upsert(
            collection_name=QDRANT_COLLECTION,
            points=qdrant_points,
            wait=True
        )
        print("Successfully uploaded all unstructured data to Local Qdrant.")

    db_session.close()
    print("\n--- ETL Process Finished ---")

if __name__ == "__main__":
    if not os.path.exists(EXCEL_PATH):
        print(f"Error: Cannot find {EXCEL_PATH}")
    elif not os.path.exists(IMAGE_DIR):
        print(f"Error: Cannot find {IMAGE_DIR}")
    elif not os.path.exists(CERT_DIR):
        print(f"Error: Cannot find {CERT_DIR}")
    else:
        run_etl()