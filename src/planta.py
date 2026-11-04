import time
import cv2
import mujoco
import mujoco.viewer

import robot
import planta_4_cintas

from src.cinta_transportadora import CintaTransportadora
from src.horno import Horno
from src.camara_inspeccion import CamaraInspeccion
from src.objeto_industrial import ObjetoIndustrial

class PlantaIndustrial:
    def __init__(self):
        self.horno = Horno(temperatura_inicial=20.0)
        self.cintas = {i: CintaTransportadora(id_cinta=i) for i in range(1, 6)}
        
        self.camaras = [
            CamaraInspeccion("cam_bottom", self.cintas[1]),
            CamaraInspeccion("cam_right",  self.cintas[2]),
            CamaraInspeccion("cam_top",    self.cintas[3]),
            CamaraInspeccion("cam_left",   self.cintas[4]),
            CamaraInspeccion("cam_oven",   self.cintas[5]),
        ]
        
        self.objetos = [
            ObjetoIndustrial(0, "caja", "cuadrado"),
            ObjetoIndustrial(1, "cilindro", "circulo"),
            ObjetoIndustrial(2, "caja", "rectangulo"),
            ObjetoIndustrial(3, "cilindro", "circulo"),
            ObjetoIndustrial(4, "caja", "rectangulo"),
        ]
        
        self.model = None
        self.data = None
        self.robot_state = None
        self.robot_ids = None

    def inicializar(self):
        xml_planta = planta_4_cintas.build_mjcf()
        self.model = robot.build_model_with_franka(xml_planta, planta_4_cintas.ROBOT_CONFIG)
        self.data = mujoco.MjData(self.model)

        self.horno.set_geom_id(self.model, "oven")
        self.robot_ids = robot.get_robot_ids(self.model)
        self.robot_state = robot.new_robot_state()

        robot.initialize_robot(self.model, self.data, self.robot_ids, self.robot_state)

        if planta_4_cintas.ROBOT_IK_TEST_MODE:
            robot.set_ik_target_rpy(
                self.model, self.robot_ids, self.robot_state,
                planta_4_cintas.ROBOT_IK_TARGET_POSITION,
                planta_4_cintas.ROBOT_IK_TARGET_RPY_DEG,
                orientation_frame=planta_4_cintas.ROBOT_IK_ORIENTATION_FRAME
            )
            mujoco.mj_forward(self.model, self.data)

        self.sincronizar_estado()

    def sincronizar_estado(self):
        """Transfiere el estado interno de los objetos POO al entorno procedural."""
        planta_4_cintas.BANDERA_CINTA_1 = self.cintas[1].esta_activa()
        planta_4_cintas.BANDERA_CINTA_2 = self.cintas[2].esta_activa()
        planta_4_cintas.BANDERA_CINTA_3 = self.cintas[3].esta_activa()
        planta_4_cintas.BANDERA_CINTA_4 = self.cintas[4].esta_activa()
        planta_4_cintas.BANDERA_CINTA_5 = self.cintas[5].esta_activa()
        planta_4_cintas.initialize_belt_rollers(self.model, self.data)

    def ejecutar(self):
        self.inicializar()

        viewer_ctx = mujoco.viewer.launch_passive(self.model, self.data)
        renderer = mujoco.Renderer(self.model, height=260, width=360)

        running = True
        paused = False
        last_cam_time = -1.0

        body_ids, dof_addrs = planta_4_cintas.get_ids(self.model)
        segments = [3, 1, 2, 3, 0]
        oven_counts = [0, 0, 0, 0, 0]
        planta_4_cintas.reset_objects(self.model, self.data, segments)

        while running and viewer_ctx.is_running():
            step_start = time.perf_counter()

            if not paused:
                self.sincronizar_estado()

                if planta_4_cintas.ROBOT_IK_TEST_MODE:
                    planta_4_cintas.apply_transport(self.model, self.data, body_ids, dof_addrs, segments, oven_counts, self.robot_state)
                    robot.control_manual_ik(self.model, self.data, self.robot_ids, self.robot_state, gripper_open=planta_4_cintas.ROBOT_IK_GRIPPER_OPEN)
                else:
                    robot.update_robot_state_machine(self.model, self.data, body_ids, self.robot_ids, self.robot_state, segments, planta_4_cintas.OBJECT_REST_Z, planta_4_cintas.ROBOT_CONFIG)
                    planta_4_cintas.apply_transport(self.model, self.data, body_ids, dof_addrs, segments, oven_counts, self.robot_state)
                    robot.control_robot_ik(self.model, self.data, self.robot_ids, self.robot_state, planta_4_cintas.ROBOT_CONFIG)
                    robot.follow_tcp_with_grasped_object(self.model, self.data, self.robot_ids, self.robot_state)

                mujoco.mj_step(self.model, self.data)
                
                planta_4_cintas.lock_object_rotations(self.model, self.data)
                planta_4_cintas.lock_cylinders_to_belt_center(self.model, self.data, segments)
                
                self.horno.actualizar_color(self.model)
                mujoco.mj_forward(self.model, self.data)

            viewer_ctx.sync()

            if (self.data.time - last_cam_time) >= (1.0 / 20.0) or paused:
                for camara in self.camaras:
                    camara.actualizar(renderer, self.data)

                mosaic = planta_4_cintas.render_camera_mosaic(renderer, self.data, paused, self.data.time, sum(oven_counts), self.robot_state)
                cv2.imshow("Camaras de la planta", mosaic)
                last_cam_time = self.data.time

                key = cv2.waitKey(1) & 0xFF
                if key in (ord('q'), 27):
                    running = False
                elif key == ord('p'):
                    paused = not paused
                elif key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5')]:
                    num = key - ord('0')
                    self.cintas[num].conmutar()

            sleep_time = self.model.opt.timestep - (time.perf_counter() - step_start)
            if sleep_time > 0: 
                time.sleep(sleep_time)

        viewer_ctx.close()
        renderer.close()
        cv2.destroyAllWindows()
