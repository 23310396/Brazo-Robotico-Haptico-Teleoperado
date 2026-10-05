# Simulador 6R

Este simulador es un banco de pruebas para la cinemática del brazo 6R del proyecto. Dibuja el manipulador como líneas y puntos, permite mover sus articulaciones con FK y también pedir una pose objetivo para probar la IK.

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

El mismo comando sirve tanto en una PC local como en GitHub Codespaces:

- **PC local con escritorio:** usa una ventana normal de Matplotlib con `TkAgg`.
- **GitHub Codespaces / entorno sin escritorio:** usa `WebAgg` y muestra la interfaz en el navegador.

### En una PC local

La terminal debe mostrar algo parecido a:

```text
Abriendo Simulador 6R con backend TkAgg...
```

y se abre una ventana con el robot 3D.

### En GitHub Codespaces

La terminal mostrará algo parecido a:

```text
Simulador 6R listo con WebAgg en el puerto 8988.
En GitHub Codespaces abre la pestaña PORTS, localiza ese puerto y elige Open in Browser.
```

Deja esa terminal corriendo mientras uses el simulador.

Después:

1. abre la pestaña **PORTS** en la parte inferior de Codespaces;
2. busca el puerto `8988`;
3. usa **Open in Browser**.

Si el puerto no aparece automáticamente, puedes agregarlo manualmente en PORTS escribiendo `8988`.

También puedes cambiar el puerto antes de ejecutar:

```bash
SIMULATOR_PORT=9000 python -m simulation.arm_6r.simulator
```

### Diagnóstico de interfaz

Si quieres revisar qué backend está usando:

```bash
python -m simulation.arm_6r.simulator --diagnose-gui
```

En Codespaces esperamos algo parecido a:

```text
Backend: WebAgg
Modo GUI: web
WebAgg: OK -> puerto 8988
```

Codespaces publica el puerto por HTTPS. El simulador corrige WebAgg para usar un WebSocket seguro (`wss://`) detrás de ese proxy. Si la página abre pero el lienzo queda completamente blanco, primero verifica que tengas la versión más reciente del repo con `git pull` y reinicia el simulador.

En una PC local normalmente esperamos:

```text
Backend: TkAgg
Modo GUI: desktop
Tk GUI: OK
```

Si sólo quieres comprobar que el simulador carga, que la FK/IK funciona y que Matplotlib puede renderizar sin abrir la interfaz:

```bash
python -m simulation.arm_6r.simulator --smoke-test
```

Si todo está bien debe aparecer:

```text
SMOKE TEST OK
```

Para ejecutar las pruebas automáticas:

```bash
python -m pytest robot/kinematics/tests
```

## Modo FK

Selecciona `FK`.

Aparecen seis sliders, uno para cada articulación `J1` a `J6`.

Al moverlos, el robot se actualiza inmediatamente. Abajo se muestran:

- posición actual del TCP;
- orientación actual en Roll, Pitch y Yaw;
- ángulos actuales de las seis articulaciones.

`Config. cero` regresa las seis articulaciones a `0°`.

La configuración cero es una referencia matemática del modelo. No debe confundirse con una posición HOME o segura del robot real.

## Modo IK

Selecciona `IK`.

Los sliders cambian a:

- `X`, `Y`, `Z`: posición deseada del TCP;
- `Roll`, `Pitch`, `Yaw`: orientación deseada del TCP.

La convención de orientación usada por la interfaz es:

```text
R = Rz(Yaw) · Ry(Pitch) · Rx(Roll)
```

Los valores de orientación se muestran en grados.

Mover el target no mueve automáticamente el robot.

### Resolver IK

Presiona `Resolver IK`.

El programa calcula las soluciones analíticas disponibles para la rama frontal del modelo. Cuando existen varias, se muestran opciones `elbow+`, `elbow-`, `wrist+` y `wrist-flip`.

Al seleccionar una solución aparece un robot fantasma con esa configuración.

La FK se vuelve a ejecutar sobre cada solución de IK para comprobar que la pose obtenida coincide con la pose pedida.

### Alcanzar

Después de elegir una solución, presiona `Alcanzar`.

El robot se anima desde su configuración actual hasta la solución elegida.

Esta animación es sólo una interpolación articular para visualizar el cambio de postura. **No es planeación de trayectoria, control de motores ni garantía de una trayectoria libre de colisiones.**

## Target no alcanzable

Si la posición/orientación pedida no tiene una solución geométrica válida para esta demo, el robot no se mueve y el estado de la IK lo reporta.

## Singularidades

La versión actual detecta la singularidad de muñeca cuando J5 hace que los ejes de J4 y J6 queden acoplados. También identifica el caso en que el centro de muñeca cae sobre el eje del hombro y J1 deja de estar determinado únicamente por la posición.

Esto todavía no sustituye un análisis completo de singularidades mediante Jacobiano.

## Opciones de visualización

`Mostrar frames` dibuja los ejes locales del modelo.

`Mostrar target` muestra u oculta la marca del objetivo.

`Trayectoria TCP` deja una línea con el recorrido del TCP mientras el robot se mueve.

`Vista iso.` devuelve la cámara a una vista isométrica cómoda.

La vista 3D también puede rotarse con el mouse usando las herramientas normales de Matplotlib.

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
├── simulator.py
├── requirements.txt
└── README.md
```

`model_6r.py` contiene la geometría sintética y los límites usados por la demo.

`forward_kinematics.py` implementa la tabla DH, la FK y las conversiones de orientación.

`inverse_kinematics.py` implementa la IK analítica y genera las ramas de solución.

`simulator.py` sólo se encarga de la interfaz, dibujo, selección de soluciones y animación.

`test_kinematics.py` comprueba casos conocidos, consistencia FK→IK→FK, targets imposibles y singularidad de muñeca.

## Qué todavía no representa este simulador

Esta primera versión no modela:

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
