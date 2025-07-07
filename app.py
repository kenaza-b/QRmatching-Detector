from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
from io import BytesIO

app = Flask(__name__)

@app.route('/', methods=['POST'])
def detect_qr_from_pdf():
    try:
        # 1. Récupérer le fichier PDF
        pdf_file = request.files.get('pdf')
        if not pdf_file:
            return jsonify({"error": "Aucun fichier reçu."}), 400

        # 2. Récupérer le texte de référence fourni par l'utilisateur
        reference_text = request.form.get('reference_text')
        if not reference_text:
            return jsonify({"error": "Paramètre 'reference_text' manquant."}), 404

        # 3. Lire les octets du PDF
        try:
            file_bytes = pdf_file.read()
        except Exception as e:
            return jsonify({"error": f"Erreur lecture fichier : {str(e)}"}), 400

        # 4. Vérifier que c’est un vrai PDF
        if not file_bytes.startswith(b'%PDF-'):
            return jsonify({"error": "Le fichier n'est pas un PDF valide."}), 400

        # 5. Ouvrir le PDF
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            return jsonify({"error": f"Impossible d'ouvrir le PDF : {str(e)}"}), 400

        if doc.page_count == 0:
            return jsonify({"error": "PDF vide."}), 404

        # 6. Convertir première page en image
        try:
            page = doc.load_page(0)
            pix = page.get_pixmap(dpi=300)
            img = Image.open(BytesIO(pix.tobytes("ppm")))
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            return jsonify({"error": f"Erreur conversion page en image : {str(e)}"}), 500

        # 7. Détecter plusieurs QR codes, choisir le plus haut
        try:
            detector = cv2.QRCodeDetector()
            retval, data_list, points, _ = detector.detectAndDecodeMulti(img_cv)

            if not retval or points is None or len(data_list) == 0:
                qr_data = None
            else:
                min_y = float('inf')
                index_choisi = -1
                for i, pts in enumerate(points):
                    y_coin_sup_gauche = pts[0][1]
                    if y_coin_sup_gauche < min_y:
                        min_y = y_coin_sup_gauche
                        index_choisi = i
                qr_data = data_list[index_choisi].strip() if index_choisi != -1 else None

        except Exception as e:
            return jsonify({"error": f"Erreur détection QR multi : {str(e)}"}), 500

        # 8. Comparer strictement QR code et texte fourni
        try:
            if qr_data and qr_data.lower() == reference_text.strip().lower():
                return jsonify({
                    "qr_data": qr_data,
                    "texte_reference": reference_text,
                    "verification": "Correspondance exacte trouvée."
                }), 200
            else:
                return jsonify({
                    "qr_data": qr_data or "Aucun QR code détecté",
                    "texte_reference": reference_text,
                    "verification": "Échec : texte différent du QR code."
                }), 400
        except Exception as e:
            return jsonify({"error": f"Erreur comparaison texte : {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Erreur inattendue : {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
