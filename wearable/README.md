# Wearable de captura de movimiento

Subsistema encargado de medir el movimiento del operador y reconstruir la pose de su miembro superior antes de enviar cualquier comando al robot.

## Objetivo de esta etapa

Antes de integrar el manipulador, el wearable debe poder validarse como un sistema independiente.

La meta funcional es:

```text
manga / soportes físicos con 3 IMUs
        ↓
adquisición y sincronización
        ↓
calibración sensor-segmento
        ↓
reconstrucción geométrica
        ↓
posición XYZ de muñeca + orientación de mano
        ↓
visualización en tiempo real del brazo reconstruido
```

La visualización deberá permitir observar, como mínimo:

- hombro como referencia;
- segmento de brazo;
- codo;
- segmento de antebrazo;
- muñeca;
- orientación de la mano;
- orientaciones relevantes de los segmentos.

La intención es comprobar visual y cuantitativamente que el modelo digital sigue al operador antes de conectar esta salida al mapping humano -> robot.

## Estado de arquitectura

### DECISIÓN — D-002

La captura del operador utiliza tres IMUs:

1. brazo;
2. antebrazo;
3. mano.

El torso se considera aproximadamente fijo durante esta etapa.

### IMPLEMENTADO

Existe un pipeline Python independiente del hardware en:

```text
sensors/pose_pipeline/
```

Actualmente permite:

- recibir orientaciones de tres segmentos;
- aplicar calibraciones conocidas;
- reconstruir posición de codo y muñeca;
- entregar orientación de mano;
- trabajar con datos sintéticos;
- ejecutar análisis de sensibilidad y pruebas automáticas.

### PROPUESTA DE ARQUITECTURA FÍSICA

Aún no adoptada como decisión final:

```text
3 IMUs
  ↓
microcontrolador
  ↓
PC
  ↓
pipeline de pose + visualización
```

La función inicial candidata del microcontrolador es adquirir, marcar temporalmente y transmitir los datos. El procesamiento de calibración, reconstrucción y visualización permanecería inicialmente en PC para facilitar depuración y validación.

No se ha seleccionado todavía el microcontrolador comercial ni la IMU final.

## Criterio para pasar a integración con el robot

No basta con que el pipeline funcione con datos ideales.

Antes de entrar de lleno al mapping hacia el robot se busca demostrar que el wearable físico puede:

1. adquirir las tres orientaciones de forma estable;
2. calibrar correctamente la relación sensor-segmento;
3. reconstruir la pose del brazo en tiempo real;
4. mostrar esa reconstrucción visualmente;
5. cuantificar error, ruido/jitter, drift, sincronización y repetibilidad;
6. mantener un comportamiento suficientemente estable para la tarea experimental.

Los límites numéricos aceptables todavía están **PENDIENTES DE VALIDACIÓN**.

## Organización

```text
wearable/
|-- README.md
|-- sensors/
|   `-- pose_pipeline/
|       |-- pipeline.py
|       |-- synthetic.py
|       |-- demo.py
|       |-- analysis/
|       `-- tests/
`-- firmware/             # futuro, cuando se seleccione MCU/hardware
```

La integración humano -> robot pertenece posteriormente al módulo de robot/mapping y no debe mezclarse con la validación básica del wearable.
