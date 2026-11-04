class CintaTransportadora:
    def __init__(self, id_cinta, velocidad=0.55):
        self.id_cinta = id_cinta
        self.velocidad = velocidad
        self.activa = True
        
    def arrancar(self):
        self.activa = True
        
    def detener(self):
        self.activa = False
        
    def conmutar(self):
        self.activa = not self.activa
        
    def esta_activa(self):
        return self.activa
