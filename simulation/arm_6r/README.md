# Simulador 6R

Este simulador es el banco de pruebas cinemático del manipulador 6R. Permite mover el brazo por articulaciones con FK, definir una pose objetivo para probar la IK y verificar las soluciones volviendo a ejecutar la FK.

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

### GitHub Codespaces

La terminal muestra el puerto usado, normalmente:

```text
8501
```

Después:

1. abre la pestaña **PORTS**;
2. busca el puerto `8501`;
3. usa **Open in Browser**;
4. deja la terminal corriendo mientras uses el simulador.

Si quieres cambiar el puerto:

```bash
SIMULATOR_PORT=9000 python -m simulation.arm_6r.simulator
```

### PC local

Ejecuta el mismo comando:

```bash
python -m simulation.arm_6r.simulator
```

Streamlit abrirá el navegador con la aplicación.

## Diagnóstico y pruebas

Para revisar el entorno:

```bash
python -m simulation.arm_6r.simulator --diagnose-gui
```

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

Selecciona **FK**.

Cada articulación `J1` a `J6` tiene dos controles sincronizados:

- un slider para explorar rápidamente;
- un campo numérico para escribir un ángulo exacto.

Los ángulos se expresan en grados y el campo numérico acepta centésimas de grado.

Modificar cualquiera de los dos controles actualiza el otro y vuelve a calcular el robot.

También se muestran:

- posición actual del TCP;
- orientación actual en Roll, Pitch y Yaw;
- ángulos actuales de las seis articulaciones.

El botón **Configuración cero** regresa:

```text
q = [0, 0, 0, 0, 0, 0]
```

Esta configuración es una referencia matemática y no debe confundirse con una posición HOME o segura del robot físico.

## Modo IK

Selecciona **IK**.

### Usar la pose FK como target

Si quieres hacer una prueba FK → IK → FK:

1. genera una postura en FK;
2. cambia a IK;
3. pulsa **Usar pose actual como target**;
4. pulsa **Configuración cero** si quieres mover el robot lejos del target;
5. pulsa **Resolver IK**;
6. selecciona una solución;
7. pulsa **Alcanzar**.

La pose se copia internamente sin redondear los valores usados por la FK.

### Controles exactos del target

Posición:

- `X`
- `Y`
- `Z`

Orientación:

- `Roll`
- `Pitch`
- `Yaw`

Cada variable tiene slider y entrada numérica sincronizados.

La convención de orientación usada por la interfaz es:

```text
R = Rz(Yaw) · Ry(Pitch) · Rx(Roll)
```

Mover el target no mueve automáticamente el robot.

## Presets de prueba

La v2 incluye cuatro casos reproducibles:

### A — alcanzable frontal

```text
X = 1.50
Y = 0.50
Z = 0.70
Roll = Pitch = Yaw = 0°
```

Debe resolverse normalmente.

### B — alcanzable lateral

```text
X = 0.90
Y = -1.10
Z = 0.80
Roll = Pitch = Yaw = 0°
```

Debe resolverse y exigir un giro lateral claro de J1.

### C — plegado extremo

```text
X = 0.35
Y = 0.05
Z = 0.30
Roll = Pitch = Yaw = 0°
```

Es geométricamente alcanzable, pero fuerza una configuración muy plegada. Sirve para recordar que esta versión todavía no modela autocolisión ni volumen físico de los eslabones.

### D — inalcanzable

```text
X = 2.60
Y = 0.00
Z = 0.25
Roll = Pitch = Yaw = 0°
```

Debe reportarse como `UNREACHABLE`.

El selector sólo carga los valores. Todavía necesitas pulsar **Resolver IK**.

## Resolver IK

Al pulsar **Resolver IK**, el programa calcula las soluciones analíticas disponibles.

Pueden aparecer ramas como:

```text
elbow+ / wrist+
elbow+ / wrist-flip
elbow- / wrist+
elbow- / wrist-flip
```

La solución seleccionada se dibuja como un robot fantasma.

La FK se ejecuta nuevamente sobre esa solución para comprobar que la pose calculada coincide con el target.

La interfaz separa tres estados:

```text
TARGET
IK
SINGULARIDAD
```

Por ejemplo:

```text
TARGET: ALCANZABLE
IK: OK
SINGULARIDAD: NO
```

o:

```text
TARGET: INALCANZABLE
IK: UNREACHABLE
SINGULARIDAD: —
```

## Alcanzar

Después de seleccionar una solución pulsa **Alcanzar**.

La v2 genera 60 configuraciones intermedias y envía la animación completa al navegador. Plotly reproduce los frames localmente, por lo que Streamlit ya no necesita volver a dibujar toda la página en cada frame.

La duración visual nominal es de aproximadamente 2.5 segundos.

La interpolación sigue siendo articular y usa una transición suavizada entre la configuración inicial y final.

> **La animación no es planificación de trayectoria ni control físico.** Puede atravesar obstáculos, regiones problemáticas o futuras geometrías del robot.

## Opciones de visualización

En la barra lateral están disponibles:

- **Mostrar frames**
- **Mostrar target**
- **Trayectoria TCP**

La vista 3D se puede rotar, acercar y alejar con el mouse.

## Dónde está cada cosa

La matemática y la interfaz se mantienen separadas:

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

`model_6r.py` contiene la geometría sintética y los límites de demo.

`forward_kinematics.py` implementa la tabla DH y la FK.

`inverse_kinematics.py` implementa la IK analítica.

`app.py` contiene la interfaz web y la animación visual.

`simulator.py` arranca la aplicación y contiene diagnóstico/smoke test.

`test_kinematics.py` comprueba casos conocidos, consistencia FK → IK → FK, targets imposibles y singularidad de muñeca.

## Qué todavía no representa este simulador

La v2 todavía no modela:

- dinámica;
- torque;
- motores o transmisiones;
- velocidad o aceleración física real;
- autocolisiones;
- colisiones con torso;
- obstáculos;
- planeación de trayectoria;
- Jacobiano completo;
- límites mecánicos reales;
- dimensiones finales;
- seguridad física del robot.

Su función sigue siendo validar y explorar la cinemática antes de cerrar la geometría física del manipulador.
