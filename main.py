from flask import Flask, request, send_from_directory, abort
import os
import threading
from log import setup_logger
from initialization import (
    initialize_app,
    DB_CONFIG,
    CZECH_DATA_PATH,
    wait_for_next_hour,
)
from data_processing.data_processing import process_data_round

backend_logger = setup_logger('backend_logger', 'app.log')
comm_logger = setup_logger('comm_logger', 'http.log')

app = Flask(__name__)

@app.before_request
def log_request():
    comm_logger.info(f"Received {request.method} request for {request.url} from {request.remote_addr}")

@app.after_request
def log_response(response):
    comm_logger.info(f"Responding with {response.status_code} to {request.remote_addr} for {request.url}")
    return response

# Route pro ziskani konkretniho colormeshe
@app.route("/get-image/<filename>")
def get_image(filename):
    image_directory = "saved_grids"

    if ".." in filename or filename.startswith("/"):
        abort(404)

    try:
        return send_from_directory(image_directory, filename)
    except FileNotFoundError:
        comm_logger.error("Požadovaný soubor nebyl nalezen.")
        abort(404)

# Route pro zjisteni dostupnych colormeshu
@app.route("/test-directory")
def test_directory():
    files = os.listdir("saved_grids")
    return str(files)


def run_flask_app():
    # Spuštění Flask aplikace v samostatném vlákně
    app.run(host="127.0.0.1", port=5000)


def data_processing_loop():
    db_ops, geo_proc, czech_rep = initialize_app(DB_CONFIG, CZECH_DATA_PATH)
    while True:
        process_data_round(db_ops, geo_proc, czech_rep)
        wait_for_next_hour()


if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    backend_logger.info("Backend processing started")
    data_processing_loop()
