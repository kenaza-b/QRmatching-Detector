import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
from io import BytesIO


def detect_qr_from_pdf_service(pdf_file, reference_text):
    # 3. Lire les octets du PDF
    try:
        file_bytes = pdf_file.read()
    except Exception as e:
        return {"error": f"Erreur lecture fichier : {str(e)}", "status": 400}

    # 4. Vérifier que c’est un vrai PDF
    if not file_bytes.startswith(b'%PDF-'):
        return {"error": "Le fichier n'est pas un PDF valide.", "status": 400}

    # 5. Ouvrir le PDF
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        return {"error": f"Impossible d'ouvrir le PDF : {str(e)}", "status": 400}

    if doc.page_count == 0:
        return {"error": "PDF vide.", "status": 404}

    # 6. Convertir première page en image
    try:
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=300)
        img = Image.open(BytesIO(pix.tobytes("ppm")))
        # Améliorer l'image avant détection QR
        from .qr_imageEnhancing_service import enchangeImage  # import relatif si besoin
        enhanced_img = enchangeImage(img)  # Assurez-vous que la fonction retourne l'image améliorée
        img_cv = cv2.cvtColor(np.array(enhanced_img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        return {"error": f"Erreur conversion page en image : {str(e)}", "status": 500}

    # 7. Détecter plusieurs QR codes, choisir le plus haut
    try:
        detector = cv2.QRCodeDetector()
        retval, data_list, points, _ = detector.detectAndDecodeMulti(img_cv)

        if not retval or points is None or len(data_list) == 0:
            return {"error": f" Aucun QR code détecté sur la page","status": 404}
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
        return {"error": f"Erreur détection QR multi : {str(e)}", "status": 500}

    # 8. Comparer strictement QR code et texte fourni
    try:
        if qr_data and qr_data.lower() == reference_text.strip().lower():
            return {
                "qr_data": qr_data,
                "texte_reference": reference_text,
                "verification": "Correspondance exacte trouvée.",
                "status": 200
            }
        else:
            return {
                "qr_data": qr_data or "Aucun QR code détecté",
                "texte_reference": reference_text,
                "verification": "Échec : texte différent du QR code.",
                "status": 400
            }
    except Exception as e:
        return {"error": f"Erreur comparaison texte : {str(e)}", "status": 500}
