from flask import Blueprint, request, jsonify
from service.qr_service import detect_qr_from_pdf_service

routes = Blueprint('routes', __name__)

@routes.route('/', methods=['POST'])
def detect_qr_from_pdf():
    try:
        pdf_file = request.files.get('pdf')
        if not pdf_file:
            return jsonify({"error": "Aucun fichier reçu."}), 400

        reference_text = request.form.get('reference_text')
        if not reference_text:
            return jsonify({"error": "Paramètre 'reference_text' manquant."}), 404

        result = detect_qr_from_pdf_service(pdf_file, reference_text)
        if 'error' in result:
            return jsonify({k: v for k, v in result.items() if k != 'status'}), result.get('status', 500)
        else:
            return jsonify({k: v for k, v in result.items() if k != 'status'}), result.get('status', 200)
    except Exception as e:
        return jsonify({"error": f"Erreur inattendue : {str(e)}"}), 500
