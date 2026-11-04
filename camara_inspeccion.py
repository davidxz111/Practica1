import cv2
import numpy as np

class CamaraInspeccion:
    def __init__(self, nombre, cinta):
        self.nombre = nombre
        self.cinta = cinta
        self.objeto_detectado = False
        self.forma_detectada = None

    def capturar(self, renderer, data):
        renderer.update_scene(data, camera=self.nombre)
        rgb = renderer.render()
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    def detectar_forma(self, frame, area_minima=300):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([0, 60, 40]), np.array([179, 255, 255]))
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contorno in contornos:
            area = cv2.contourArea(contorno)
            if area < area_minima:
                continue

            perimetro = cv2.arcLength(contorno, True)
            if perimetro <= 0:
                continue

            aprox = cv2.approxPolyDP(contorno, 0.03 * perimetro, True)
            vertices = len(aprox)
            x, y, w, h = cv2.boundingRect(aprox)
            circularidad = (4.0 * np.pi * area) / (perimetro * perimetro)

            if vertices == 4:
                return "cuadrado" if 0.85 <= (w / float(h)) <= 1.15 else "rectangulo"
            elif vertices >= 6 and circularidad > 0.72:
                return "circulo"
            elif circularidad > 0.78:
                return "circulo"
                
        return None

    def actualizar(self, renderer, data):
        imagen = self.capturar(renderer, data)
        forma_actual = self.detectar_forma(imagen)
        detectado_ahora = forma_actual is not None

        # Detiene la cinta solo la primera vez que ve la pieza para permitir la reanudación manual posterior
        if detectado_ahora and not self.objeto_detectado:
            self.cinta.detener()

        self.objeto_detectado = detectado_ahora
        self.forma_detectada = forma_actual

        if detectado_ahora:
            cv2.putText(imagen, forma_actual.upper(), (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
        return imagen
