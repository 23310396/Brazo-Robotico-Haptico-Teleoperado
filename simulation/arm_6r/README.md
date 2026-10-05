# Simulador 6R

Este simulador es un banco de pruebas para la cinemática del brazo 6R del proyecto. Permite mover el manipulador por articulaciones con FK y también definir una pose objetivo para probar la IK.

> **Importante:** la geometría actual es sintética: `L1 = 1.0`, `L2 = 1.0` y `LT = 0.25`. Son valores de demo y no representan dimensiones físicas del brazo final.

## Qué necesitas

Python 3.10 o más reciente.

Desde la raíz del repositorio instala las dependencias:

```bash
python -m pip install -r simulation/arm_6r/requirements.txt
```

## Cómo ejecutarlo

También desde la raíz del repositorio:

```bash
python -m simulation.arm_6r.simulator
```

El simulador se abre en el navegador usando Streamlit + Plotly.

### Si estás en GitHub Codespaces

La terminal mostrará el puerto usado, normalmente:

```text
8501
```

Después:

1. abre la pestaña **PORTS** en Codespaces;
2. busca el puerto `8501`;
3. usa **Open in Browser**;
4. deja la terminal corriendo mientras uses el simulador.

Si quieres usar otro puerto:

```bash
SIMULATOR_PORT=9000 python -m simulation.arm_6r.simulator
```

### Si estás en una PC local

Ejecuta el mismo comando:

```bash
python -m simulation.arm_6r.simulator
```

Streamlit abrirá el navegador con el simulador.

## Diagnóstico

Para comprobar qué entorno está usando:

```bash
python -m simulation.arm_6r.simulator --diagnose-gui
```

Debe mostrar Python, versión de Streamlit, versión de Plotly y el puerto del simulador.

Para validar la FK/IK y las dependencias sin abrir la interfaz:

```bash
python -m simulation.arm_6r.simulator --smoke-test
```

Si todo está bien debe aparecer:

```text
SMOKE TEST OK
```

Para correr las pruebas automáticas:

```bash
python -m pytest robot/kinematics/tests
```

## Modo FK

Selecciona **FK** en la barra lateral.

Aparecen seis sliders:

- `J1`
- `J2`
- `J3`
- `J4`
- `J5`
- `J6`

Al moverlos, el robot se actualiza en 3D.

También se muestra:

- posición actual del TCP;
- orientación actual en Roll, Pitch y Yaw;
- ángulos actuales de las seis articulaciones.

El botón **Configuración cero** regresa las seis articulaciones a `0°`.

La configuración cero es una referencia matemática. No debe confundirse con una posición HOME o segura del robot real.

## Modo IK

Selecciona **IK**.

En la barra lateral puedes modificar:

- `X`, `Y`, `Z`: posición deseada del TCP;
- `Roll`, `Pitch`, `Yaw`: orientación deseada del TCP.

La convención de orientación de la interfaz es:

```text
R = Rz(Yaw) · Ry(Pitch) · Rx(Roll)
```

Mover el target no mueve automáticamente el robot.

### Resolver IK

Presiona **Resolver IK**.

Si hay soluciones válidas aparecen las distintas ramas, por ejemplo:

```text
elbow+ / wrist+
elbow+ / wrist-flip
elbow- / wrist+
elbow- / wrist-flip
```

La solución seleccionada se dibuja como un robot fantasma.

La FK se ejecuta sobre la solución para comprobar que la pose obtenida coincide con la pose pedida.

### Alcanzar

Después de elegir una solución presiona **Alcanzar**.

El robot se anima desde la configuración actual hasta la solución elegida.

La animación es sólo una interpolación articular para visualizar la transición. **No es planeación de trayectoria, control de motores ni garantía de una trayectoria libre de colisiones.**

## Opciones de visualización

En la barra lateral están disponibles:

- **Mostrar frames**
- **Mostrar target**
- **Trayectoria TCP**

La vista 3D de Plotly se puede rotar, acercar y alejar directamente con el mouse.

## Dónde está cada cosa

La matemática está separada de la interfaz:

```text
robot/kinematics/
├── model_6r.py
├── forward_kinematics.py
├── inverse_kinematics.py
└── tests/
    └── test_kinematics.py

simulation/arm_6r/
├── app.py
├── simulator.py
├── requirements.txt
└── README.md
```

`model_6r.py` contiene la geometría sintética y los límites usados por la demo.

`forward_kinematics.py` implementa la tabla DH y la FK.

`inverse_kinematics.py` implementa la IK analítica y genera las ramas de solución.

`app.py` contiene la interfaz web.

`simulator.py` arranca la aplicación y conserva los comandos de diagnóstico y smoke test.

`test_kinematics.py` comprueba casos conocidos, consistencia FK→IK→FK, targets imposibles y singularidad de muñeca.

## Qué todavía no representa este simulador

Esta versión no modela:

- dinámica;
- torque;
- motores o transmisiones;
- velocidad real;
- aceleración real;
- colisiones con el torso;
- obstáculos;
- planeación de trayectoria;
- límites mecánicos reales;
- seguridad física del robot.

Su función actual es validar y entender la geometría, FK e IK antes de cerrar las dimensiones físicas del manipulador.
