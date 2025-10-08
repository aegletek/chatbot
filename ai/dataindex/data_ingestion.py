import os
import sys
import shutil
import argparse
from datetime import datetime

# Add the parent directory to the system path to allow for sibling imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.DataExtract.data_retrieval import ingest_data
from ai.config import LANDING_ZONE_DIR, PROCESSED_DIR, FAILED_DIR, LOG_FILE, SCHEMA_DIR

# Ensure Processed and Failed directories exist
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(FAILED_DIR, exist_ok=True)

def log_message(message: str) -> None:
    """Logs a message with a timestamp to the log file and prints it."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    with open(LOG_FILE, 'a') as f:
        f.write(full_message + '\n')

def process_files(update: bool) -> None:
    """
    Processes all supported files (.pdf, .docx, .txt) in the LandingZone directory.
    - Ingests data from each file.
    - Moves the file to the Processed directory on success.
    - Moves the file to the Failed directory on failure.
    """
    log_message(f"Starting data ingestion process in {'UPDATE' if update else 'APPEND'} mode...")
    
    supported_extensions = ['.pdf', '.docx', '.txt']
    files_in_landing_zone = [
        f for f in os.listdir(LANDING_ZONE_DIR) 
        if f.lower().endswith(tuple(supported_extensions))
    ]
    
    if not files_in_landing_zone:
        log_message("No new document files found in the LandingZone.")
        return

    for filename in files_in_landing_zone:
        source_path = os.path.join(LANDING_ZONE_DIR, filename)
        log_message(f"Processing file: {filename}")
        
        try:
            schema_path = None
            base_filename = os.path.splitext(filename)[0]
            index_name = base_filename.capitalize().replace('_', '').replace('-', '')

            if not update:  # Append mode
                expected_schema_filename = f"{base_filename}.json"
                schema_path = os.path.join(SCHEMA_DIR, expected_schema_filename)
                
                if not os.path.exists(schema_path):
                    raise FileNotFoundError(f"Schema file not found for '{filename}'. Expected at: {schema_path}")

            # Perform the ingestion
            ingest_data(source_path, index_name, schema_path)
            
            # Move the file to the Processed directory
            destination_path = os.path.join(PROCESSED_DIR, filename)
            shutil.move(source_path, destination_path)
            log_message(f"Successfully processed and moved '{filename}' to Processed directory.")
            
        except Exception as e:
            log_message(f"ERROR: Failed to process '{filename}'. Reason: {e}")
            
            # Move the file to the Failed directory
            destination_path = os.path.join(FAILED_DIR, filename)
            shutil.move(source_path, destination_path)
            log_message(f"Moved '{filename}' to Failed directory.")

    log_message("Data ingestion process finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process PDF files and ingest them into Weaviate.")
    parser.add_argument(
        '--update',
        type=lambda x: (str(x).lower() == 'true'),
        default=True,
        help="Set to 'True' for UPDATE mode (use main schema), 'False' for APPEND mode (use alternate schema from JSON)."
    )
    args = parser.parse_args()
    
    process_files(args.update)
