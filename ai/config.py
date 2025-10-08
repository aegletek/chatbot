
import os

# Get the absolute path of the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Define directory paths
LANDING_ZONE_DIR = os.path.join(PROJECT_ROOT, 'ai', 'dataindex', 'LandingZone')
PROCESSED_DIR = os.path.join(PROJECT_ROOT, 'ai', 'dataindex', 'Processed')
FAILED_DIR = os.path.join(PROJECT_ROOT, 'ai', 'dataindex', 'Failed')
SCHEMA_DIR = os.path.join(PROJECT_ROOT, 'ai', 'dataindex', 'Schema')
LOG_FILE = os.path.join(PROJECT_ROOT, 'ai', 'dataindex', 'ingestion_log.txt')
ENV_PATH = os.path.join(PROJECT_ROOT, 'ai', 'variables', '.env')
