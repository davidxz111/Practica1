# Práctica: Refactorización POO de Simulación Industrial (MuJoCo y OpenCV)

Práctica desarrollada para la asignatura de Programación Orientada a Objetos (POO)

## Tecnologías utilizadas

* Python 3.x
* MuJoCo (Motor de física y simulación 3D)
* OpenCV (`opencv-python`) (Procesamiento de visión artificial y detección de formas)
* NumPy

## Estructura del proyecto

El repositorio está organizado separando el punto de entrada de la lógica de negocio y las clases del sistema:

```text
Practica1/
│
├── src/                          <-- Clases y módulos de la simulación
│   ├── camara_inspeccion.py      <-- Captura de fotogramas y filtrado HSV con OpenCV
│   ├── cinta_transportadora.py   <-- Control independiente de marcha y parada
│   ├── horno.py                  <-- Gestión de temperatura y actualización de color
│   └── objeto_industrial.py      <-- Propiedades lógicas y geométricas de las piezas
│
├── main.py                       <-- Punto de entrada principal de la aplicación
└── README.md                     <-- Documentación del proyecto
```

## Cómo clonar y ejecutar el proyecto en Linux

Sigue estos pasos en tu terminal para descargar el repositorio, configurar el entorno e iniciar la simulación:

### 1. Clonar el repositorio
```bash
git clone https://github.com/davidxz111/Practica1.git
cd Practica1
```

### 2. Crear y activar un entorno virtual (Recomendado)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar las dependencias
Instala las librerías necesarias ejecutando el siguiente comando:
```bash
pip install mujoco opencv-python numpy
```

### 4. Ejecutar la simulación
Lanza el programa principal desde la raíz del proyecto:
```bash
python3 main.py
```
