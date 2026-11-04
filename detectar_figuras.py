import cv2
import numpy as np


def detectar_figuras_geometricas(frame, area_minima=300):
    """
    Detecta las figuras geométricas de los objetos sobre la cinta.

    Figuras detectadas:
        - cuadrado
        - rectangulo
        - circulo

    Parameters
    ----------
    frame : np.ndarray
        Imagen BGR obtenida desde la cámara.
    area_minima : int
        Área mínima de un contorno para considerarlo objeto.

    Returns
    -------
    detecciones : list
        Lista de diccionarios:
        {
            "forma": str,
            "centro": (cx, cy),
            "area": float,
            "bbox": (x, y, w, h)
        }

    imagen_resultado : np.ndarray
        Imagen con contornos y etiquetas.
    """

    imagen_resultado = frame.copy()

    # ---------------------------------------------------------
    # 1. Convertir de BGR a HSV
    # ---------------------------------------------------------
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # ---------------------------------------------------------
    # 2. Separar objetos coloreados de la cinta oscura
    #
    # Los objetos de la práctica son rojo, azul, verde,
    # amarillo, morado, etc.
    # ---------------------------------------------------------
    mask = cv2.inRange(
        hsv,
        np.array([0, 60, 40]),
        np.array([179, 255, 255])
    )

    # ---------------------------------------------------------
    # 3. Limpiar la máscara
    # ---------------------------------------------------------
    kernel = np.ones((5, 5), np.uint8)

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    # ---------------------------------------------------------
    # 4. Buscar contornos
    # ---------------------------------------------------------
    contornos, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    detecciones = []

    # ---------------------------------------------------------
    # 5. Analizar cada objeto
    # ---------------------------------------------------------
    for contorno in contornos:

        area = cv2.contourArea(contorno)

        if area < area_minima:
            continue

        perimetro = cv2.arcLength(contorno, True)

        if perimetro <= 0:
            continue

        # -----------------------------------------------------
        # Aproximación poligonal
        # -----------------------------------------------------
        aproximacion = cv2.approxPolyDP(
            contorno,
            0.03 * perimetro,
            True
        )

        vertices = len(aproximacion)

        # -----------------------------------------------------
        # Bounding box
        # -----------------------------------------------------
        x, y, w, h = cv2.boundingRect(aproximacion)

        relacion_aspecto = w / float(h)

        # -----------------------------------------------------
        # Circularidad
        #
        # círculo ideal ≈ 1
        # -----------------------------------------------------
        circularidad = (
            4.0 * np.pi * area /
            (perimetro * perimetro)
        )

        # -----------------------------------------------------
        # Clasificación de la forma
        # -----------------------------------------------------

        if vertices == 4:

            if 0.85 <= relacion_aspecto <= 1.15:
                forma = "cuadrado"

            else:
                forma = "rectangulo"

        elif vertices >= 6 and circularidad > 0.72:

            forma = "circulo"

        else:

            # Segunda comprobación para cilindros que debido
            # al renderizado no produzcan un contorno perfecto.
            if circularidad > 0.78:
                forma = "circulo"
            else:
                forma = "desconocido"

        # -----------------------------------------------------
        # Centro del objeto
        # -----------------------------------------------------
        momentos = cv2.moments(contorno)

        if momentos["m00"] != 0:

            cx = int(
                momentos["m10"] /
                momentos["m00"]
            )

            cy = int(
                momentos["m01"] /
                momentos["m00"]
            )

        else:

            cx = x + w // 2
            cy = y + h // 2

        # -----------------------------------------------------
        # Guardar detección
        # -----------------------------------------------------
        deteccion = {
            "forma": forma,
            "centro": (cx, cy),
            "area": area,
            "bbox": (x, y, w, h),
            "vertices": vertices,
            "circularidad": circularidad
        }

        detecciones.append(deteccion)

        # -----------------------------------------------------
        # Dibujar resultado
        # -----------------------------------------------------
        cv2.drawContours(
            imagen_resultado,
            [contorno],
            -1,
            (0, 255, 0),
            2
        )

        cv2.rectangle(
            imagen_resultado,
            (x, y),
            (x + w, y + h),
            (255, 255, 255),
            2
        )

        cv2.circle(
            imagen_resultado,
            (cx, cy),
            4,
            (0, 0, 255),
            -1
        )

        texto = forma.upper()

        cv2.putText(
            imagen_resultado,
            texto,
            (x, max(y - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

    return detecciones, imagen_resultado, mask