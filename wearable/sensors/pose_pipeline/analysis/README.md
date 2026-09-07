# Análisis de sensibilidad V1

Esta carpeta contiene análisis sintéticos del pipeline de pose. Su función es estudiar cómo errores controlados en las orientaciones y en la calibración afectan la posición y orientación reconstruidas.

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

## Formato de las demos

Los análisis mantienen el formato:

```text
TENEMOS
CALCULAMOS
OBTENEMOS
```

Los valores utilizados son **escenarios sintéticos de análisis**. No representan especificaciones de una IMU real ni límites aceptados por el proyecto.

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
- un error residual de calibración se propaga de la misma forma que un error angular equivalente en la orientación usada por el pipeline.

Los criterios físicos de error aceptable permanecen **PENDIENTES DE VALIDACIÓN** y deberán derivarse de la tarea experimental y los requerimientos del sistema.
