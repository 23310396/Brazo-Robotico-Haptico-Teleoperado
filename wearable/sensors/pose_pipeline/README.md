# Pipeline de pose del operador

Primer módulo funcional de D-002. Su objetivo es comprobar en software la reconstrucción de la pose de la mano antes de seleccionar IMUs comerciales.

## Qué entra

Tres orientaciones en quaternion `[w, x, y, z]`:

- brazo;
- antebrazo;
- mano.

Cada orientación puede venir después de una IMU real, de un archivo o de datos sintéticos. El núcleo matemático no conoce la marca del sensor.

## Qué sale

`HandPoseEstimate` contiene:

- posición de la muñeca en el frame humano `H`, en metros;
- orientación de la mano en quaternion;
- posición calculada del codo;
- diferencia temporal máxima entre las tres muestras.

La salida termina en el frame humano. El mapping humano -> robot y la IK se implementarán después en 03.

## Organización

```text
pose_pipeline/
|-- pipeline.py                    # núcleo matemático
|-- synthetic.py                   # generación de entradas sintéticas
|-- demo.py                        # demostración didáctica V0
|-- analysis/                      # análisis de sensibilidad V1
|   |-- README.md
|   |-- angular_sensitivity.py
|   |-- calibration_sensitivity.py
|   |-- noise_jitter.py
|   |-- drift.py
|   `-- desynchronization.py
`-- tests/                         # pruebas automáticas de todo el módulo
    |-- test_pipeline.py
    |-- test_angular_sensitivity.py
    |-- test_calibration_sensitivity.py
    |-- test_noise_jitter.py
    |-- test_drift.py
    `-- test_desynchronization.py
```

El código de análisis no se mezcla con el pipeline que después consumirá el robot.

## Modelo geométrico

Con el hombro como origen y el eje local +X de cada segmento apuntando hacia su extremo distal:

```text
p_codo   = R_brazo * [L_brazo, 0, 0]
p_muneca = p_codo + R_antebrazo * [L_antebrazo, 0, 0]
R_mano   = orientación calibrada de la IMU de mano
```

No se obtiene posición mediante doble integración de aceleración.

## Calibración en esta versión

La versión V0 aplica calibraciones conocidas. Esto permite validar primero la geometría sin mezclar errores del algoritmo de calibración con errores de reconstrucción.

Para cada segmento se aplica:

```text
q_H_B = q_H_N * q_N_S * q_S_B
```

La estimación física de `q_S_B` mediante calibración funcional + estática queda para una etapa posterior.

## Demo explicativa V0

`demo.py` está pensada para entender la lógica sin tener que leer primero todo el código.

Ejecutar:

```bash
python wearable/sensors/pose_pipeline/demo.py
```

La demo mantiene el formato:

```text
TENEMOS
CALCULAMOS
OBTENEMOS
```

## Análisis de sensibilidad V1

Los análisis que perturban deliberadamente las entradas se guardan en `analysis/`.

### Error angular general

```bash
python wearable/sensors/pose_pipeline/analysis/angular_sensitivity.py
```

Estudia cuánto error de posición/orientación aparece cuando el pipeline recibe orientaciones con errores angulares sintéticos.

### Error residual de calibración

```bash
python wearable/sensors/pose_pipeline/analysis/calibration_sensitivity.py
```

Estudia por separado:

```text
offset físico de montaje
-
offset estimado por calibración
=
error residual de calibración
```

### Ruido y jitter

```bash
python wearable/sensors/pose_pipeline/analysis/noise_jitter.py
```

Simula orientaciones que fluctúan alrededor del valor real y cuantifica cómo ese ruido se transforma en jitter de posición de muñeca y orientación de mano, tanto con el brazo quieto como durante una trayectoria sintética.

### Drift angular

```bash
python wearable/sensors/pose_pipeline/analysis/drift.py
```

Simula una deriva angular progresiva mientras la pose física permanece fija. Permite cuantificar cómo el error acumulativo en brazo, antebrazo, mano o las tres IMUs se transforma en error de posición y orientación con el paso del tiempo.

### Desincronización dinámica

```bash
python wearable/sensors/pose_pipeline/analysis/desynchronization.py
```

Compara una pose ideal, donde las tres orientaciones corresponden al mismo instante, contra reconstrucciones donde los sensores pertenecen a instantes distintos durante movimiento.

También separa desincronización relativa de retardo común: tres sensores pueden estar perfectamente sincronizados entre sí y aun así representar una pose antigua por latencia.

Los tiempos, velocidades, niveles de ruido y tasas de drift utilizados son escenarios sintéticos y **no representan especificaciones de una IMU real ni requisitos adoptados por el proyecto**.

## Pruebas automáticas

Todas las pruebas del módulo están contenidas en `tests/`.

Ejecutar desde la raíz del repositorio:

```bash
python -m unittest discover -s wearable/sensors/pose_pipeline/tests -v
```

Las pruebas cubren geometría base, quaternions, calibración conocida, timestamps, sensibilidad angular, errores residuales de calibración, ruido/jitter reproducible, drift sintético y desincronización dinámica.

GitHub Actions ejecuta automáticamente este mismo conjunto cuando cambia contenido dentro de `wearable/`.

## Relación con la validación física

El objetivo antes de conectar el robot es que la manga física alimente este pipeline y que una visualización en tiempo real permita observar los segmentos reconstruidos del brazo y sus orientaciones.

Eso permitirá comparar el movimiento físico con el modelo digital y medir estabilidad, error, ruido, drift, sincronización y repetibilidad antes de pasar al mapping humano -> robot.

## Cierre de la fase sintética

La caracterización sintética del pipeline cubre ya los efectos principales que necesitamos entender antes de comprar hardware:

- error angular;
- error residual de calibración;
- ruido/jitter;
- drift;
- desincronización temporal durante movimiento;
- diferencia conceptual entre skew interno y latencia común.

No se propone seguir creando pruebas sintéticas indefinidamente. La repetibilidad real y los niveles físicos de ruido, drift y sincronización se medirán con el wearable construido.

El siguiente incremento del proyecto es definir requisitos de adquisición de las 3 IMUs y utilizarlos para seleccionar IMU y microcontrolador con documentación oficial.

## Criterio de validación V0

Los casos sintéticos ideales deben coincidir con el resultado analítico con tolerancia numérica de `1e-9` para posiciones/rotaciones comprobadas en las pruebas.

Este criterio valida exclusivamente la matemática y el software; no representa todavía la precisión física exigida al wearable.
