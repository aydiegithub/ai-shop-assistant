from flask import Flask, request, render_template, redirect, url_for
from backend.data_ingestion import DataIngestion
from database.aws_s3_connection import upload_file_to_s3
import os

app = Flask(__name__)
data_ingestor = DataIngestion()

@app.route("/")
def upload_page():
    return render_template("upload.html")

@app.route("/upload-csv", methods=["POST"])
def upload_csv():
    file = request.files.get("file")
    if file:
        temp_path = f"temp_{file.filename}"
        file.save(temp_path)

        # Upload to S3
        upload_file_to_s3(temp_path, file.filename)
        os.remove(temp_path)

        # Trigger ingestion from S3
        data_ingestor.run_ingestion_from_s3(file.filename)

        return {"message": f"{file.filename} uploaded to S3 and ingested to D1 successfully."}
    return {"error": "No file uploaded."}

if __name__ == "__main__":
    app.run(debug=True)