# Análisis de sensibilidad V1

Esta carpeta contiene análisis sintéticos del pipeline de pose. Su función es estudiar cómo errores controlados en las orientaciones de entrada afectan la posición y orientación reconstruidas.

No contiene código necesario para operar el wearable real. El pipeline funcional permanece en el nivel superior de `pose_pipeline/`.

## Sensibilidad angular

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

Se prueban los siguientes valores:

```text
0.5°, 1°, 2°, 5°, 10°
```

Estos valores son **escenarios de análisis**, no especificaciones de una IMU ni límites aceptados por el proyecto.

Se estudian cuatro casos:

1. error sólo en brazo;
2. error sólo en antebrazo;
3. mismo error en brazo y antebrazo;
4. error sólo en mano.

Para cada caso se muestra:

```text
TENEMOS
CALCULAMOS
OBTENEMOS
```

y se reporta:

- error angular inyectado;
- error de posición de muñeca en mm;
- error de orientación de mano en grados.

## Ejecutar en Codespaces

Desde la raíz del repositorio:

```bash
python wearable/sensors/pose_pipeline/analysis/angular_sensitivity.py
```

También puede abrirse el archivo y utilizar el botón **Run**.

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

La V1 todavía no valida hardware real. Busca caracterizar la sensibilidad matemática del modelo y comprobar, entre otras cosas, que:

- un error angular en brazo o antebrazo puede transformarse en error cartesiano de muñeca;
- un error compartido por ambos segmentos puede producir un desplazamiento mayor;
- un error exclusivamente en la IMU de mano no debe modificar la posición de muñeca con la arquitectura actual, pero sí la orientación de salida.

Los criterios físicos de error aceptable permanecen **PENDIENTES DE VALIDACIÓN** y deberán derivarse de la tarea experimental y los requerimientos del sistema.
