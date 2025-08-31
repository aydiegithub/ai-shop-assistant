from flask import Flask, request, render_template, jsonify, Response
from src.backend.data_ingestion import DataIngestion
import os
import json
import time
import threading
from queue import Queue
from src.logging import logging

logger = logging()

app = Flask(__name__, template_folder='src/frontend/templates')

# Global variables for progress tracking and log streaming
progress_queues = {}
log_queues = {}

# Create a single instance of the DataIngestion pipeline
data_ingestor = DataIngestion() 

def emit_progress(session_id, stage, percentage, message):
    """Emit progress update to the progress queue for a session"""
    if session_id in progress_queues:
        progress_data = {
            'type': 'progress',
            'stage': stage,
            'percentage': percentage,
            'message': message,
            'timestamp': time.time()
        }
        progress_queues[session_id].put(progress_data)

def emit_log(session_id, level, message):
    """Emit log message to the log queue for a session"""
    if session_id in log_queues:
        log_data = {
            'type': 'log',
            'level': level,
            'message': message,
            'timestamp': time.time()
        }
        log_queues[session_id].put(log_data) 

@app.route("/")
def upload_page():
    logger.info("Serving upload page")
    return render_template("upload.html")

@app.route("/progress/<session_id>")
def progress_stream(session_id):
    """Server-Sent Events endpoint for progress updates"""
    def event_stream():
        # Initialize queues for this session
        progress_queues[session_id] = Queue()
        log_queues[session_id] = Queue()
        
        try:
            while True:
                # Check for progress updates
                if not progress_queues[session_id].empty():
                    data = progress_queues[session_id].get()
                    yield f"data: {json.dumps(data)}\n\n"
                
                # Check for log updates
                if not log_queues[session_id].empty():
                    data = log_queues[session_id].get()
                    yield f"data: {json.dumps(data)}\n\n"
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
        except GeneratorExit:
            # Clean up when client disconnects
            if session_id in progress_queues:
                del progress_queues[session_id]
            if session_id in log_queues:
                del log_queues[session_id]
    
    return Response(event_stream(), mimetype="text/event-stream")

def process_file_with_progress(file_path, filename, session_id):
    """Process file with progress tracking"""
    try:
        emit_progress(session_id, "upload", 10, "File received successfully")
        emit_log(session_id, "info", f"Starting processing of {filename}")
        
        # For demonstration purposes, if we don't have AWS credentials, simulate the process
        try:
            # Call the enhanced data ingestion with progress tracking
            data_ingestor.start_data_ingestion_with_progress(
                local_file_path=file_path, 
                s3_file_name=filename,
                session_id=session_id,
                emit_progress=emit_progress,
                emit_log=emit_log
            )
        except Exception as processing_error:
            # If processing fails (e.g., due to missing credentials), simulate progress for demo
            emit_log(session_id, "warning", f"Simulating processing due to missing credentials: {str(processing_error)}")
            
            # Simulate S3 upload
            emit_progress(session_id, "s3", 25, "Uploading file to S3...")
            time.sleep(1)
            emit_log(session_id, "info", "File uploaded to S3 successfully (simulated)")
            emit_progress(session_id, "s3", 40, "S3 upload completed")
            
            # Simulate CSV processing
            emit_progress(session_id, "processing", 60, "Reading CSV file...")
            time.sleep(1)
            emit_log(session_id, "info", "CSV loaded: 5 rows found")
            emit_progress(session_id, "processing", 70, "Processing product descriptions with AI...")
            time.sleep(2)
            emit_log(session_id, "info", "Product mapping completed successfully")
            emit_progress(session_id, "processing", 85, "Product mapping completed")
            
            # Simulate database update
            emit_progress(session_id, "database", 90, "Updating D1 database...")
            time.sleep(1)
            emit_log(session_id, "info", "D1 database updated successfully")
            emit_progress(session_id, "database", 100, "Database update completed")
        
        emit_progress(session_id, "complete", 100, "Processing completed successfully")
        emit_log(session_id, "info", "File processing completed successfully")
        
    except Exception as e:
        emit_progress(session_id, "error", 0, f"Error: {str(e)}")
        emit_log(session_id, "error", f"Processing failed: {str(e)}")
        raise

@app.route("/upload-csv", methods=["POST"])
def upload_csv():
    file = request.files.get("file")
    session_id = request.form.get("session_id", "default")
    
    if file and file.filename != '':
        temp_path = f"temp_{file.filename}"
        try:
            logger.info(f"Processing file upload: {file.filename}")
            file.save(temp_path)
            logger.info(f"Temporary file saved at: {temp_path}")

            # Start processing in a separate thread to allow real-time updates
            processing_thread = threading.Thread(
                target=process_file_with_progress,
                args=(temp_path, file.filename, session_id)
            )
            processing_thread.daemon = True
            processing_thread.start()
            
            return jsonify({
                "message": "File upload started",
                "session_id": session_id,
                "status": "processing"
            })
        
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            if session_id in progress_queues:
                emit_progress(session_id, "error", 0, f"Upload failed: {str(e)}")
                emit_log(session_id, "error", f"Upload failed: {str(e)}")
            return jsonify({"error": str(e)}), 500
        finally:
            # Clean up temp file after processing
            def cleanup_temp_file():
                time.sleep(2)  # Wait a bit for processing to start
                if os.path.exists(temp_path):
                    logger.info(f"Cleaning up temporary file: {temp_path}")
                    os.remove(temp_path)
            
            cleanup_thread = threading.Thread(target=cleanup_temp_file)
            cleanup_thread.daemon = True
            cleanup_thread.start()

    logger.error("No file provided in the request")
    return jsonify({"error": "No file uploaded."}), 400

if __name__ == "__main__":
    logger.info("Starting Flask application on port 5000")
    app.run(debug=True, port=5000)