class Horno:
    def __init__(self, temperatura_inicial=20.0):
        self.numero_piezas = 0
        self.temperatura = temperatura_inicial
        self.geom_id = None

    def set_geom_id(self, model, geom_name="oven"):
        import mujoco
        self.geom_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, geom_name)
        
    def registrar_pieza(self):
        self.numero_piezas += 1

    def aumentar_temperatura(self, incremento):
        self.temperatura += incremento

    def disminuir_temperatura(self, decremento):
        self.temperatura -= decremento

    def obtener_temperatura(self):
        return self.temperatura

    def actualizar_color(self, model):
        if self.geom_id is None or self.geom_id < 0:
            return
            
        if self.temperatura < 50.0:
            color = [0.1, 0.3, 1.0, 1.0]  # Azul
        elif self.temperatura < 100.0:
            color = [1.0, 0.6, 0.1, 1.0]  # Naranja
        else:
            color = [1.0, 0.1, 0.1, 1.0]  # Rojo
            
        geom_start = model.body_geomadr[self.geom_id]
        geom_num = model.body_geomnum[self.geom_id]
        
        if geom_num > 0:
            model.geom_rgba[geom_start] = color
