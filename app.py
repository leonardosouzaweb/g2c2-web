from flask import Flask, render_template, request, send_file
import os
from file_processor import process_file  # Import the processing function
import pandas as pd
import traceback  # For detailed error messages
from urllib.parse import quote
from datetime import datetime  # Import datetime to add timestamp

# Define the Flask app
app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Create the directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('error.html', message="No file part found in the request"), 400
    
    file = request.files['file']
    if file.filename == '':
        return render_template('error.html', message="No file selected for upload"), 400
    
    if file and file.filename.endswith('.csv'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        try:
            file.save(filepath)
            
            # Gerar um timestamp para incluir no nome do arquivo processado
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            original_filename = os.path.splitext(file.filename)[0]
            processed_filename = f"{original_filename}_processed_{timestamp}.csv"
            processed_filepath = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
            
            # Call the process_file function from file_processor.py and save the result
            processed_filepath = process_file(filepath)
            
            if processed_filepath:
                # Renomeia o arquivo processado para incluir o timestamp e salvar no local correto
                os.rename(processed_filepath, processed_filepath)
                filename = os.path.basename(processed_filepath)
                return render_template('success.html', processed_file=quote(filename))
            else:
                return render_template('error.html', message="File processing failed. Please check the file format and try again."), 500
        except Exception as e:
            error_details = traceback.format_exc()  # Get detailed traceback
            formatted_message = str(e).replace("\n", "<br>")  # Replace newlines with <br> for better HTML formatting
            return render_template('error.html', message=f"An unexpected error occurred: {formatted_message}", details=error_details), 500
    else:
        return render_template('error.html', message="Invalid file format. Only CSV files are allowed."), 400

@app.route('/download/<path:filepath>')
def download_file(filepath):
    # O caminho do arquivo precisa ser codificado corretamente
    filepath = os.path.join(app.config['PROCESSED_FOLDER'], filepath)
    try:
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return render_template('error.html', message=f"Error downloading file: {str(e)}"), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=8000)
