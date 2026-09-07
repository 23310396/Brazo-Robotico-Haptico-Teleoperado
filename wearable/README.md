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
- cuantificar sensibilidad a error angular;
- analizar error residual de calibración;
- simular ruido/jitter;
- simular drift;
- estudiar desincronización dinámica y distinguirla de latencia común;
- comprobar sensibilidad con perturbaciones 3D/multieje;
- estudiar error por longitudes incorrectas de brazo/antebrazo;
- ejecutar pruebas automáticas mediante GitHub Actions.

La batería actual contiene 62 pruebas automáticas. Esta evidencia valida software y matemática sintética, no hardware físico.

La caracterización sintética se considera suficiente para pasar al siguiente bloque. No se propone seguir agregando perturbaciones sintéticas sin una necesidad concreta revelada por hardware o validación física.

### REQUISITOS DE ADQUISICIÓN

Se creó:

```text
requirements/acquisition_requirements.md
```

Este documento fija el contrato que debe cumplir la futura adquisición física y separa requisitos obligatorios, propuestas de arquitectura y parámetros numéricos todavía pendientes de validación.

Entre otros puntos exige:

- 3 canales identificables de orientación 3D;
- quaternion y convención de frames documentados;
- timestamps cercanos a la adquisición;
- sincronización medible;
- frecuencia y latencia medibles;
- detección de datos inválidos/perdidos;
- compatibilidad real de bus para 3 sensores;
- calibración sensor-segmento independiente;
- longitudes corporales configurables;
- logging para D-006;
- alimentación y montaje estables.

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

Como MVP se propone evaluar primero USB/serial cableado MCU→PC para reducir variables de comunicación durante la validación física. La interfaz definitiva aún no está adoptada.

No se ha seleccionado todavía el microcontrolador comercial ni la IMU final.

## Siguiente incremento

La siguiente etapa es comparar IMUs y microcontroladores contra `requirements/acquisition_requirements.md` utilizando datasheets y documentación oficial.

No se deben adoptar valores de frecuencia, skew, latencia o precisión sólo porque un componente los anuncie. Los límites físicos finales se cerrarán mediante literatura, tarea experimental y mediciones reales.

La repetibilidad relevante para D-006 se medirá físicamente con el wearable construido, no mediante una simulación adicional que sólo repita datos generados por software.

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
|-- requirements/
|   `-- acquisition_requirements.md
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
