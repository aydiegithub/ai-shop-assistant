from flask import Flask, request, render_template, jsonify
from src.backend.data_ingestion import DataIngestion
import os
from src.logging import logging

logger = logging()

app = Flask(__name__, template_folder='src/frontend/templates')

# Create a single instance of the DataIngestion pipeline
data_ingestor = DataIngestion() 

@app.route("/")
def upload_page():
    logger.info("Serving upload page")
    return render_template("upload.html")

@app.route("/upload-csv", methods=["POST"])
def upload_csv():
    file = request.files.get("file")
    if file and file.filename != '':
        temp_path = f"temp_{file.filename}"
        try:
            logger.info(f"Processing file upload: {file.filename}")
            file.save(temp_path)
            logger.info(f"Temporary file saved at: {temp_path}")

            # --- The Fix ---
            # Now, we only call the data_ingestor and give it the local file path.
            # It will handle everything else internally.
            logger.info(f"Handing off to Data Ingestor for file: {file.filename}")
            data_ingestor.start_data_ingestion(local_file_path=temp_path, s3_file_name=file.filename)
            
            logger.info(f"Successfully processed file: {file.filename}")
            return jsonify({"message": f"{file.filename} uploaded to S3 and ingested to D1 successfully."})
        
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            return jsonify({"error": str(e)}), 500
        finally:
            # This 'finally' block ensures the temp file is always cleaned up
            if os.path.exists(temp_path):
                logger.info(f"Cleaning up temporary file: {temp_path}")
                os.remove(temp_path)

    logger.error("No file provided in the request")
    return jsonify({"error": "No file uploaded."}), 400

if __name__ == "__main__":
    logger.info("Starting Flask application on port 5000")
    app.run(debug=True, port=5000)