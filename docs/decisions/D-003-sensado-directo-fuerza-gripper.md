# D-003 — Sensado directo de fuerza en el gripper

**Estado:** DECISIÓN ADOPTADA  
**Área principal:** Fuerza / Gripper  
**Impacta:** diseño del gripper, instrumentación, acondicionamiento, métricas experimentales y feedback háptico

## Contexto

Una de las hipótesis del proyecto requiere analizar la fuerza de agarre y el efecto de la retroalimentación háptica. Para que esa variable pueda utilizarse como métrica experimental, debe medirse de forma cuantificable y suficientemente repetible.

## Decisión

Utilizar **sensado directo de fuerza mediante strain gauges / load cell**, integrando el elemento sensor en la trayectoria mecánica de transmisión de fuerza del gripper.

Para el MVP se prioriza medir la componente asociada a la **fuerza de agarre escalar**. No se adopta medición multiaxial como requisito mientras la tarea experimental no la justifique.

Cadena conceptual:

`gripper → strain gauge/load cell → acondicionamiento + ADC → filtrado → fuerza cuantitativa → mapping háptico → actuador vibrotáctil`

## Alternativas consideradas

### A. FSR

**Ventaja:** integración sencilla.  
**Limitación:** se mantiene como alternativa secundaria por problemas documentados de histéresis y repetibilidad para una medición cuantitativa rigurosa.

### B. Strain gauge / load cell — SELECCIONADA

Permite diseñar una cadena de medición directa de fuerza y realizar calibración cuantitativa para la métrica experimental.

### C. Corriente o torque del actuador

Se conserva como señal indirecta o auxiliar. No se adopta como variable principal de fuerza de la tesis.

## Justificación

La decisión prioriza una medición directamente relacionada con la fuerza mecánica del gripper y compatible con una validación metrológica básica antes de utilizar los datos en el experimento.

La instrumentación deberá diseñarse junto con la mecánica del gripper; no debe añadirse como accesorio sin analizar la trayectoria real de carga.

## Relación con otras decisiones

- **D-004:** la magnitud medida será la variable principal para generar el feedback vibrotáctil.
- **D-005:** el tipo de montaje del manipulador no modifica el principio de sensado, aunque el gripper y su payload deberán dimensionarse en conjunto con el brazo.

## Pendiente de validación

- Geometría del elemento sensor.
- Rango de fuerza en N.
- Número de sensores.
- Ubicación mecánica definitiva.
- Amplificador/acondicionamiento.
- ADC.
- Frecuencia de muestreo.
- Procedimiento de calibración.
- Linealidad.
- Histéresis.
- Repetibilidad.
- Resolución.
- Incertidumbre.
- Saturación.
- Efecto de cargas fuera del eje de medición.

## Trazabilidad

- Contexto Maestro v7 — D-003 y bloque de sensado de fuerza.
- Estado del Arte v1 — sensado de fuerza y retroalimentación háptica.
- **P-FRC-002 — Kuang, Lou & Song (2018), _Design and Fabrication of a Novel Force Sensor for Robot Grippers_, DOI 10.1109/JSEN.2017.2788015.** Fuente aceptada de acceso restringido; utilizar solamente detalles verificables.
- La matriz maestra de fuentes deberá conservar el resto de trabajos que respaldan o contrastan load cells, strain gauges, FSR y estimación indirecta.

## Criterio de validación de la decisión

Antes de usar la fuerza como métrica experimental, el subsistema deberá demostrar calibración, repetibilidad y rango suficientes para la tarea definida.
