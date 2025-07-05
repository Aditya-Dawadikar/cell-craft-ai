import os
import boto3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import traceback

# Optional: scikit-learn if needed
import sklearn

# === Read environment variables passed from the Kubernetes Job ===
SESSION_ID = os.getenv('SESSION_ID')
COMMIT_ID = os.getenv('COMMIT_ID')
CODE_S3_PATH = os.getenv('CODE_S3_PATH')       # e.g., session_files/<session_id>/<commit_id>/<commit_id>_code.py
INPUT_S3_PATH = os.getenv('INPUT_S3_PATH')     # e.g., session_files/<session_id>/<commit_id>/<commit_id>.csv
OUTPUT_S3_PREFIX = os.getenv('OUTPUT_S3_PREFIX')  # e.g., session_files/<session_id>/<commit_id>/
BUCKET_NAME = os.getenv('BUCKET_NAME', 'your-bucket-name')  # You can pass this too or hardcode if fixed

# Local paths
WORK_DIR = '/app'
CODE_FILE = os.path.join(WORK_DIR, 'user_code.py')
INPUT_FILE = os.path.join(WORK_DIR, 'input.csv')
COMMIT_DIR = os.path.join(WORK_DIR, 'commit_output')

os.makedirs(COMMIT_DIR, exist_ok=True)

# Initialize S3 client
s3 = boto3.client('s3')

try:
    print("Downloading code and input CSV from S3...")

    # Download user code
    s3.download_file(BUCKET_NAME, CODE_S3_PATH, CODE_FILE)

    # Download input CSV
    s3.download_file(BUCKET_NAME, INPUT_S3_PATH, INPUT_FILE)

    # Load DataFrame into memory
    df = pd.read_csv(INPUT_FILE)

    # Prepare execution environment
    safe_globals = {
        "__builtins__": __builtins__,
        "pd": pd,
        "np": np,
        "sklearn": sklearn,
        "plt": plt,
        "sns": sns
    }

    local_vars = {
        "df": df,
        "commit_dir": COMMIT_DIR
    }

    print("Executing user code...")

    # Read and execute code
    with open(CODE_FILE, 'r') as f:
        user_code = f.read()

    exec(user_code, safe_globals, local_vars)

    # Retrieve the possibly transformed DataFrame
    df = local_vars.get('df', df)

    # Save transformed CSV
    output_csv_name = f"{COMMIT_ID}.csv"
    output_csv_path = os.path.join(COMMIT_DIR, output_csv_name)
    df.to_csv(output_csv_path, index=False)

    print("Uploading all generated files to S3...")

    # Upload all files from commit_dir to S3
    for root, dirs, files in os.walk(COMMIT_DIR):
        for file in files:
            local_file_path = os.path.join(root, file)
            s3_key = f"{OUTPUT_S3_PREFIX}{file}"
            s3.upload_file(local_file_path, BUCKET_NAME, s3_key)
            print(f"Uploaded {file} to s3://{BUCKET_NAME}/{s3_key}")

    print("Job completed successfully.")

except Exception as e:
    print("Error occurred during job execution:")
    traceback.print_exc()
    raise e
