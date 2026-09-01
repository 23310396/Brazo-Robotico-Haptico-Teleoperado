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

## Modelo geométrico

Con el hombro como origen y el eje local +X de cada segmento apuntando hacia su extremo distal:

```text
p_codo   = R_brazo * [L_brazo, 0, 0]
p_muneca = p_codo + R_antebrazo * [L_antebrazo, 0, 0]
R_mano   = orientación calibrada de la IMU de mano
```

No se obtiene posición mediante doble integración de aceleración.

## Calibración en esta versión

La versión V0 **aplica calibraciones conocidas**. Esto permite validar primero la geometría sin mezclar errores del algoritmo de calibración con errores de reconstrucción.

Para cada segmento se aplica:

```text
q_H_B = q_H_N * q_N_S * q_S_B
```

La estimación física de `q_S_B` mediante calibración funcional + estática queda para una etapa posterior.

## Demo explicativa

Además de las pruebas automáticas existe `demo.py`, pensada para entender la lógica sin tener que leer primero todo el código.

La demo imprime en cada ejemplo tres secciones:

```text
TENEMOS     -> datos de entrada
CALCULAMOS  -> operación geométrica que se realiza
OBTENEMOS   -> posición/orientación calculada
```

Ejecutar desde la raíz del repositorio:

```bash
python wearable/sensors/pose_pipeline/demo.py
```

También se puede abrir `demo.py` en Codespaces y usar el botón **Run**.

La demo incluye:

1. brazo y antebrazo totalmente extendidos: `0.30 + 0.25 = 0.55 m`;
2. codo a 90 grados: muñeca en `(0.30, 0.00, 0.25) m`;
3. giro de 30 grados sólo en la mano: cambia la orientación pero no la posición de la muñeca.

La demo es didáctica. No sustituye las pruebas automáticas.

## Pruebas automáticas

Todas las pruebas del módulo están contenidas en `tests/`.

Ejecutar desde la raíz del repositorio:

```bash
python -m unittest discover -s wearable/sensors/pose_pipeline/tests -v
```

Casos cubiertos:

1. brazo y antebrazo rectos: 0.30 m + 0.25 m = 0.55 m;
2. codo a 90 grados: muñeca en `(0.30, 0.00, 0.25)` m;
3. rotar sólo la mano cambia orientación pero no posición de muñeca;
4. una IMU montada con offset conocido se corrige mediante calibración;
5. `q` y `-q` producen la misma rotación;
6. se reporta el skew temporal de las tres muestras;
7. longitudes no físicas se rechazan;
8. quaternion de norma cero se rechaza;
9. composición sensor + corrección recupera identidad.

## Criterio de validación V0

Los casos sintéticos ideales deben coincidir con el resultado analítico con tolerancia numérica de `1e-9` para posiciones/rotaciones comprobadas en las pruebas.

Este criterio valida exclusivamente la matemática y el software; no representa todavía la precisión física exigida al wearable.
