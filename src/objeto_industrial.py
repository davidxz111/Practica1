class ObjetoIndustrial:
    def __init__(self, id_objeto, tipo="desconocido", forma="desconocido", segmento_inicial=0):
        self.id_objeto = id_objeto
        self.tipo = tipo
        self.forma = forma
        self.segmento = segmento_inicial

    def actualizar_segmento(self, nuevo_segmento):
        self.segmento = nuevo_segmento

    def obtener_segmento(self):
        return self.segmento
