from flask import Flask, request, render_template, jsonify
from src.backend.data_ingestion import DataIngestion
import os
from src.logging import logging
import threading
import time
import json
from datetime import datetime

logger = logging()

app = Flask(__name__, template_folder='src/frontend/templates')

# Create a single instance of the DataIngestion pipeline
data_ingestor = DataIngestion() 

# Global variable to track upload progress
upload_status = {
    "status": "idle",  # idle, uploading, processing, completed, error
    "progress": 0,
    "message": "",
    "logs": [],
    "filename": "",
    "start_time": None
}

# Global lock to prevent multiple simultaneous uploads
upload_lock = threading.Lock()

def update_progress(status, progress, message):
    """Update the global progress status"""
    upload_status["status"] = status
    upload_status["progress"] = progress
    upload_status["message"] = message
    upload_status["logs"].append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "message": message,
        "level": "info" if status != "error" else "error"
    })

@app.route("/")
def upload_page():
    logger.info("Serving upload page")
    return render_template("upload.html")

@app.route("/upload-csv", methods=["POST"])
def upload_csv():
    global upload_status
    
    # Check if another upload is in progress
    if not upload_lock.acquire(blocking=False):
        return jsonify({"error": "Another upload is already in progress."}), 429
    
    try:
        file = request.files.get("file")
        if file and file.filename != '':
            # Reset status
            upload_status = {
                "status": "uploading",
                "progress": 0,
                "message": "Starting upload...",
                "logs": [],
                "filename": file.filename,
                "start_time": datetime.now()
            }
            
            # Use absolute path for temp file
            temp_path = os.path.abspath(f"temp_{int(time.time())}_{file.filename}")
            
            def process_upload():
                try:
                    update_progress("uploading", 10, f"Saving file: {file.filename}")
                    
                    # Save the file with explicit file handling
                    try:
                        # Read file content into memory first
                        file_content = file.read()
                        
                        # Write to temp file
                        with open(temp_path, 'wb') as temp_file:
                            temp_file.write(file_content)
                        
                        # Verify file was written correctly
                        if not os.path.exists(temp_path):
                            raise Exception(f"File {temp_path} was not created")
                        
                        file_size = os.path.getsize(temp_path)
                        if file_size == 0:
                            raise Exception(f"File {temp_path} is empty")
                        
                        update_progress("uploading", 20, f"File saved successfully: {temp_path} ({file_size} bytes)")
                        
                    except Exception as save_error:
                        raise Exception(f"Failed to save file: {save_error}")
                    
                    update_progress("processing", 30, "Initializing data ingestion pipeline...")
                    
                    update_progress("processing", 50, "Uploading to S3...")
                    
                    update_progress("processing", 70, "Processing data and mapping products...")
                    
                    # This will handle the actual processing
                    data_ingestor.start_data_ingestion(local_file_path=temp_path, s3_file_name=file.filename)
                    
                    update_progress("processing", 90, "Updating D1 database...")
                    
                    update_progress("completed", 100, f"Successfully processed {file.filename}!")
                    
                except Exception as e:
                    error_msg = f"Error processing file {file.filename}: {str(e)}"
                    logger.error(error_msg)
                    update_progress("error", 0, error_msg)
                finally:
                    # Clean up temp file
                    try:
                        if os.path.exists(temp_path):
                            # Wait a bit longer to ensure all file operations are complete
                            time.sleep(3)
                            os.remove(temp_path)
                            update_progress(upload_status["status"], upload_status["progress"], "Temporary files cleaned up")
                    except Exception as cleanup_error:
                        logger.warning(f"Could not clean up temp file {temp_path}: {cleanup_error}")
                    finally:
                        # Release the lock when processing is complete
                        upload_lock.release()
            
            # Start processing in background thread
            thread = threading.Thread(target=process_upload)
            thread.daemon = True
            thread.start()
            
            return jsonify({"message": "Upload started", "status": "processing"})
        
        else:
            logger.error("No file provided in the request")
            return jsonify({"error": "No file uploaded."}), 400
            
    except Exception as e:
        upload_lock.release()  # Make sure to release lock on error
        return jsonify({"error": str(e)}), 500

@app.route("/upload-status")
def upload_status_endpoint():
    """Endpoint to get current upload status"""
    return jsonify(upload_status)

@app.route("/logs")
def get_logs():
    """Endpoint to get recent logs"""
    return jsonify({"logs": upload_status["logs"][-20:]})  # Return last 20 log entries

if __name__ == "__main__":
    logger.info("Starting Flask application on port 5000")
    # Disable debug mode to prevent multiple instances
    app.run(debug=False, port=5000, threaded=True)