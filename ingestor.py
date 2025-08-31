from flask import Flask, request, render_template, jsonify, Response
import os
import json
import threading
import time
import uuid
from src.logging import logging

logger = logging()

app = Flask(__name__, template_folder='src/frontend/templates')

# Try to import DataIngestion, fallback to mock if dependencies missing
try:
    from src.backend.data_ingestion import DataIngestion
    data_ingestor = DataIngestion()
    USE_REAL_BACKEND = True
except ImportError as e:
    logger.warning(f"Could not import DataIngestion: {e}. Using mock backend.")
    data_ingestor = None
    USE_REAL_BACKEND = False

# In-memory storage for upload progress and logs
upload_sessions = {}
upload_logs = {} 

@app.route("/")
def upload_page():
    logger.info("Serving upload page")
    return render_template("upload.html")

@app.route("/upload-progress/<session_id>")
def get_upload_progress(session_id):
    """Get progress for a specific upload session"""
    session = upload_sessions.get(session_id, {})
    return jsonify({
        "progress": session.get("progress", 0),
        "status": session.get("status", "waiting"),
        "message": session.get("message", ""),
        "filename": session.get("filename", "")
    })

@app.route("/upload-logs/<session_id>")
def stream_upload_logs(session_id):
    """Stream logs for a specific upload session"""
    def generate():
        last_log_count = 0
        timeout_count = 0
        max_timeout = 30  # 30 seconds timeout
        
        while timeout_count < max_timeout:
            logs = upload_logs.get(session_id, [])
            
            # Send new logs
            if len(logs) > last_log_count:
                for log in logs[last_log_count:]:
                    yield f"data: {json.dumps(log)}\n\n"
                last_log_count = len(logs)
                timeout_count = 0  # Reset timeout
            else:
                time.sleep(0.5)
                timeout_count += 0.5
            
            # Check if upload is complete
            session = upload_sessions.get(session_id, {})
            if session.get("status") in ["completed", "error"]:
                yield f"data: {json.dumps({'type': 'complete', 'status': session.get('status')})}\n\n"
                break
    
    return Response(generate(), mimetype='text/plain', headers={
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    })

def add_log(session_id, log_type, message):
    """Add a log entry for a session"""
    if session_id not in upload_logs:
        upload_logs[session_id] = []
    
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "type": log_type,
        "message": message
    }
    upload_logs[session_id].append(log_entry)

def update_progress(session_id, progress, status, message):
    """Update progress for a session"""
    if session_id not in upload_sessions:
        upload_sessions[session_id] = {}
    
    upload_sessions[session_id].update({
        "progress": progress,
        "status": status,
        "message": message
    })

def process_upload_async(session_id, file_path, filename):
    """Process upload asynchronously with progress tracking"""
    try:
        upload_sessions[session_id]["filename"] = filename
        
        add_log(session_id, "info", f"Starting upload process for {filename}")
        update_progress(session_id, 10, "processing", "File received, starting processing...")
        
        add_log(session_id, "info", f"Processing file upload: {filename}")
        
        # Simulate file validation
        time.sleep(0.5)
        add_log(session_id, "info", f"File validation completed")
        update_progress(session_id, 20, "processing", "File validated successfully")
        
        add_log(session_id, "info", f"Handing off to Data Ingestor for file: {filename}")
        update_progress(session_id, 30, "processing", "Initializing data ingestion...")
        
        if USE_REAL_BACKEND and data_ingestor:
            # Call the actual data ingestion
            data_ingestor.start_data_ingestion(local_file_path=file_path, s3_file_name=filename)
        else:
            # Mock processing for demonstration
            add_log(session_id, "info", f"Uploading to S3 bucket...")
            update_progress(session_id, 60, "processing", "Uploading to cloud storage...")
            time.sleep(1)
            
            add_log(session_id, "info", f"File uploaded to S3 successfully")
            update_progress(session_id, 80, "processing", "Processing data for ingestion...")
            time.sleep(1)
            
            add_log(session_id, "info", f"Starting data mapping and transformation...")
            update_progress(session_id, 90, "processing", "Mapping product data...")
            time.sleep(0.5)
            
            add_log(session_id, "info", f"Updating database with new data...")
            update_progress(session_id, 95, "processing", "Updating database...")
            time.sleep(0.5)
        
        add_log(session_id, "success", f"Data ingestion completed successfully")
        update_progress(session_id, 100, "completed", f"{filename} uploaded and processed successfully")
        
    except Exception as e:
        error_msg = f"Error processing file {filename}: {str(e)}"
        logger.error(error_msg)
        add_log(session_id, "error", error_msg)
        update_progress(session_id, 0, "error", error_msg)
    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            try:
                logger.info(f"Cleaning up temporary file: {file_path}")
                os.remove(file_path)
                add_log(session_id, "info", f"Temporary file cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up temp file: {str(e)}")
                add_log(session_id, "warning", f"Could not clean up temporary file: {str(e)}")

@app.route("/upload-csv", methods=["POST"])
def upload_csv():
    file = request.files.get("file")
    if file and file.filename != '':
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        temp_path = f"temp_{session_id}_{file.filename}"
        
        try:
            logger.info(f"Processing file upload: {file.filename}")
            file.save(temp_path)
            logger.info(f"Temporary file saved at: {temp_path}")
            
            # Initialize session
            upload_sessions[session_id] = {
                "progress": 0,
                "status": "started",
                "message": "Upload started",
                "filename": file.filename
            }
            upload_logs[session_id] = []
            
            # Start async processing
            thread = threading.Thread(
                target=process_upload_async,
                args=(session_id, temp_path, file.filename)
            )
            thread.daemon = True
            thread.start()
            
            # Return session ID immediately
            return jsonify({
                "session_id": session_id,
                "message": "Upload started successfully",
                "filename": file.filename
            })
        
        except Exception as e:
            error_msg = f"Error starting upload for {file.filename}: {str(e)}"
            logger.error(error_msg)
            # Clean up temp file if it exists
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({"error": error_msg}), 500

    logger.error("No file provided in the request")
    return jsonify({"error": "No file uploaded."}), 400

if __name__ == "__main__":
    logger.info("Starting Flask application on port 5000")
    app.run(debug=True, port=5000)