from PIL import Image, ImageEnhance

def enchangeImage(image_produite):
    # Convertir en niveaux de gris (souvent mieux pour QR)
    img_gray = image_produite.convert('L')

    # Contraste modéré
    enhancer = ImageEnhance.Contrast(img_gray)
    img_enhanced = enhancer.enhance(1.5)

    # Netteté modérée
    enhancer = ImageEnhance.Sharpness(img_enhanced)
    img_enhanced = enhancer.enhance(2.0)

    # Pas de flou (éviter pour QR)
    # img_cv = np.array(img_enhanced)
    # Pas de cv2.GaussianBlur

    # Sauvegarder l’image finale
    # img_enhanced.save("page1_enhanced.png")
    print("Image améliorée sauvegardée sous 'page1_enhanced.png'")
    return img_enhanced