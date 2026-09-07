# Análisis de sensibilidad V1

Esta carpeta contiene análisis sintéticos del pipeline de pose. Su función es estudiar cómo errores controlados en orientaciones, calibración, tiempo y parámetros geométricos afectan la posición y orientación reconstruidas.

No contiene código necesario para operar el wearable real. El pipeline funcional permanece en el nivel superior de `pose_pipeline/`.

## 1. Sensibilidad angular

`angular_sensitivity.py` estudia errores angulares sintéticos alrededor de Z para brazo, antebrazo, ambos y mano.

```bash
python wearable/sensors/pose_pipeline/analysis/angular_sensitivity.py
```

## 2. Sensibilidad a error de calibración

`calibration_sensitivity.py` separa offset físico de montaje y error residual de calibración.

```bash
python wearable/sensors/pose_pipeline/analysis/calibration_sensitivity.py
```

## 3. Ruido y jitter

`noise_jitter.py` simula ruido angular variable tanto con pose estática como durante movimiento y reporta métricas RMS, desviación estándar, pico a pico y máximos.

```bash
python wearable/sensors/pose_pipeline/analysis/noise_jitter.py
```

## 4. Drift angular

`drift.py` estudia una deriva angular progresiva sin aplicar filtros, magnetómetro, clutch ni recenter.

```bash
python wearable/sensors/pose_pipeline/analysis/drift.py
```

## 5. Desincronización dinámica

`desynchronization.py` distingue:

1. desincronización relativa entre las tres IMUs durante movimiento;
2. retardo común, donde las tres IMUs siguen sincronizadas entre sí pero representan una pose anterior.

```bash
python wearable/sensors/pose_pipeline/analysis/desynchronization.py
```

## 6. Sensibilidad espacial / multieje

`multiaxis_sensitivity.py` corrige una limitación de los primeros análisis: una IMU mide orientación 3D y no basta con comprobar perturbaciones alrededor de un único eje.

Se parte de una pose tridimensional no trivial y se inyecta el mismo error alrededor de:

```text
X local
Y local
Z local
eje diagonal (1,1,1)
```

Se analiza por separado brazo, antebrazo y mano.

Una consecuencia geométrica importante del modelo es que un giro puramente alrededor del eje longitudinal local +X de brazo o antebrazo no desplaza el extremo de ese segmento; errores que inclinan dicho eje sí pueden desplazar codo/muñeca. En la IMU de mano, el error angular aparece como error de orientación de salida.

```bash
python wearable/sensors/pose_pipeline/analysis/multiaxis_sensitivity.py
```

## 7. Sensibilidad a longitudes de segmentos

`segment_length_sensitivity.py` estudia un error distinto a los de la IMU: utilizar una longitud incorrecta para brazo o antebrazo.

Las orientaciones se mantienen ideales y sólo se modifica la longitud introducida al modelo. Se reporta error de posición de codo y muñeca.

Escenarios sintéticos:

```text
-20, -10, -5, 0, +5, +10 y +20 mm
```

Estos valores no representan todavía incertidumbre real de medición del operador.

```bash
python wearable/sensors/pose_pipeline/analysis/segment_length_sensitivity.py
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

- errores angulares en brazo/antebrazo pueden convertirse en error cartesiano de muñeca;
- errores de mano afectan directamente la orientación de salida;
- la calibración correcta puede compensar un offset físico conocido;
- el error residual de calibración se propaga a la reconstrucción;
- ruido angular puede producir jitter aun con el operador quieto;
- drift puede producir error acumulativo;
- desincronización relativa y latencia común son fenómenos distintos;
- el comportamiento se mantiene coherente en orientaciones tridimensionales y perturbaciones en varios ejes;
- una longitud de segmento mal medida genera error cartesiano aunque las orientaciones sean perfectas.

## Criterio de cierre de la caracterización sintética

Con estos bloques se consideran cubiertos los riesgos matemáticos principales conocidos antes de seleccionar hardware:

1. geometría base;
2. error angular;
3. calibración residual;
4. ruido/jitter;
5. drift;
6. desincronización/latencia;
7. orientación 3D multieje;
8. error de longitudes de segmento.

No se agregarán pruebas sintéticas únicamente para aumentar cobertura. Una prueba adicional requerirá un riesgo concreto revelado por la selección de hardware, la adquisición real o la validación física.

La repetibilidad relevante para D-006 debe medirse con el wearable físico.

El siguiente paso es derivar requisitos de adquisición para 3 IMUs y, con ellos, iniciar la selección justificada de IMU y microcontrolador.

Los criterios físicos de error aceptable permanecen **PENDIENTES DE VALIDACIÓN**.
