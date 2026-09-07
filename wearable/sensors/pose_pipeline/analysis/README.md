# Análisis de sensibilidad V1

Esta carpeta contiene análisis sintéticos del pipeline de pose. Su función es estudiar cómo errores controlados en las orientaciones, la calibración y la variación temporal afectan la posición y orientación reconstruidas.

No contiene código necesario para operar el wearable real. El pipeline funcional permanece en el nivel superior de `pose_pipeline/`.

## 1. Sensibilidad angular

Archivo:

```text
angular_sensitivity.py
```

El análisis parte de un caso sintético simple:

- brazo: 0.30 m;
- antebrazo: 0.25 m;
- ambos inicialmente extendidos hacia +X;
- calibración ideal;
- errores angulares artificiales alrededor de Z.

Se prueban:

```text
0.5°, 1°, 2°, 5°, 10°
```

Casos:

1. error sólo en brazo;
2. error sólo en antebrazo;
3. mismo error en brazo y antebrazo;
4. error sólo en mano.

Ejecutar:

```bash
python wearable/sensors/pose_pipeline/analysis/angular_sensitivity.py
```

## 2. Sensibilidad a error de calibración

Archivo:

```text
calibration_sensitivity.py
```

Este análisis separa:

```text
orientación real del segmento
+
offset físico de montaje de la IMU
-
offset estimado durante calibración
=
orientación reconstruida
```

La demo principal usa el ejemplo discutido durante el desarrollo:

```text
antebrazo real                 = 45°
offset físico de montaje       = 10°
lectura equivalente de la IMU  = 55°
offset estimado                = 8°
orientación reconstruida       = 47°
error residual                 = 2°
```

Con el antebrazo sintético de 0.25 m, ese error residual de 2° produce aproximadamente 8.726 mm de error en la posición reconstruida de la muñeca.

También se prueban errores residuales de:

```text
0°, 0.5°, 1°, 2°, 5°
```

por separado en brazo, antebrazo y mano.

Ejecutar:

```bash
python wearable/sensors/pose_pipeline/analysis/calibration_sensitivity.py
```

## 3. Ruido y jitter

Archivo:

```text
noise_jitter.py
```

Este análisis ya no aplica un error constante. Simula lecturas que fluctúan alrededor de la orientación real.

Se estudian dos situaciones:

1. **pose estática:** el brazo no se mueve, pero las tres orientaciones reciben ruido angular independiente;
2. **movimiento:** el antebrazo recorre una trayectoria ideal y las orientaciones medidas se perturban alrededor de ella.

Los niveles sintéticos utilizados son:

```text
sigma = 0°, 0.1°, 0.5°, 1°, 2°
```

El ruido se genera con distribución gaussiana de media cero y semilla fija. La semilla sólo sirve para que la simulación sea reproducible: Codespaces y GitHub Actions deben obtener exactamente los mismos resultados.

Se reportan métricas como:

- RMS del error de posición de muñeca;
- desviación estándar del error de posición;
- pico a pico del error de posición;
- RMS del error de orientación de mano;
- desviación estándar y pico a pico del error de orientación;
- error máximo durante una trayectoria en movimiento.

Ejecutar:

```bash
python wearable/sensors/pose_pipeline/analysis/noise_jitter.py
```

Los valores de sigma son **escenarios sintéticos de análisis**. No representan especificaciones de una IMU real ni límites aceptados por el proyecto.

## 4. Drift angular

Archivo:

```text
drift.py
```

Este análisis estudia un error que no fluctúa alrededor del valor real, sino que se acumula progresivamente con el tiempo mientras la pose física permanece fija.

Modelo sintético:

```text
drift acumulado = tasa de drift * tiempo
```

Se analiza por separado:

1. drift sólo en brazo;
2. drift sólo en antebrazo;
3. drift sólo en mano;
4. el mismo drift en las tres IMUs.

Las tasas sintéticas usadas son:

```text
0, 0.01, 0.05, 0.10 y 0.25 °/s
```

durante un escenario de 60 s. Estos valores son únicamente parámetros de simulación: **no representan especificaciones de una IMU real ni criterios de aceptación del proyecto**.

Se reportan:

- drift angular acumulado al final;
- RMS del error de posición;
- error máximo de posición;
- error final de posición;
- RMS del error de orientación;
- error máximo de orientación;
- error final de orientación.

La simulación no aplica filtro, magnetómetro, clutch ni recenter. Primero se caracteriza el problema sin mitigación.

Ejecutar:

```bash
python wearable/sensors/pose_pipeline/analysis/drift.py
```

## 5. Desincronización dinámica

Archivo:

```text
desynchronization.py
```

Estudia la diferencia entre dos problemas temporales distintos:

1. **desincronización relativa:** brazo, antebrazo y mano corresponden a instantes diferentes durante movimiento;
2. **retardo común:** las tres IMUs están sincronizadas entre sí, pero todas representan una pose anterior al instante de referencia.

Para la desincronización relativa se prueban escenarios sintéticos de:

```text
0, 5, 10, 20 y 50 ms
```

con velocidades angulares sintéticas diferentes para brazo, antebrazo y mano. Los valores no son requisitos ya adoptados ni representan movimiento máximo del usuario.

El análisis permite observar que:

- un skew temporal con el operador quieto no altera por sí solo la pose;
- durante movimiento, el mismo skew puede generar error de posición y orientación;
- el efecto aumenta con la velocidad de movimiento;
- un retardo común puede tener `sensor_time_skew_s = 0` y aun así producir error de seguimiento por latencia.

Ejecutar:

```bash
python wearable/sensors/pose_pipeline/analysis/desynchronization.py
```

## Formato de las demos

Los análisis mantienen el formato:

```text
TENEMOS
CALCULAMOS
OBTENEMOS
```

## Pruebas automáticas

Las pruebas permanecen centralizadas en:

```text
wearable/sensors/pose_pipeline/tests/
```

Para ejecutar todo el conjunto:

```bash
python -m unittest discover -s wearable/sensors/pose_pipeline/tests -v
```

## Qué valida esta etapa

La V1 todavía no valida hardware real. Busca caracterizar la sensibilidad matemática del modelo y comprobar que:

- un error angular en brazo o antebrazo puede transformarse en error cartesiano de muñeca;
- un error exclusivamente en la IMU de mano afecta la orientación y no la posición de muñeca con la arquitectura actual;
- una IMU físicamente montada con offset puede reconstruir correctamente el segmento si la calibración compensa ese offset;
- el problema relevante es el **error residual de calibración**, no simplemente que la IMU esté montada con cierto ángulo;
- un error residual de calibración se propaga de la misma forma que un error angular equivalente en la orientación usada por el pipeline;
- ruido angular variable puede convertirse en jitter de posición/orientación incluso cuando el operador está quieto;
- durante movimiento puede cuantificarse cuánto se separa la trayectoria reconstruida de la ideal;
- una deriva angular progresiva puede convertirse en error acumulativo de posición u orientación según el segmento afectado;
- la desincronización relativa y la latencia común son fenómenos distintos y deberán producir requisitos distintos en la adquisición física.

## Cierre de la caracterización sintética

Con geometría, sensibilidad angular, calibración residual, ruido/jitter, drift y desincronización dinámica cubiertos, no se propone seguir agregando perturbaciones sintéticas indefinidamente.

La repetibilidad relevante para D-006 deberá medirse con el wearable físico. El siguiente paso es derivar requisitos de adquisición para 3 IMUs y, con ellos, iniciar la selección justificada de IMU y microcontrolador.

Los criterios físicos de error aceptable permanecen **PENDIENTES DE VALIDACIÓN** y deberán derivarse de la tarea experimental, los componentes seleccionados y las mediciones reales.
