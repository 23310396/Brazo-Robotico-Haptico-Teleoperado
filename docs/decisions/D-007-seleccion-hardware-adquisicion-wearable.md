# D-007 — Selección de hardware de adquisición del wearable

**Estado:** DECISIÓN ADOPTADA  
**Fecha:** 20 de septiembre de 2026  
**Área principal:** Wearable / Sensado / Adquisición embebida  
**Impacta:** D-002, D-006, firmware, comunicaciones, BOM, validación física y diseño mecánico del wearable

## Contexto

Después de cerrar la caracterización sintética del pipeline y definir `wearable/requirements/acquisition_requirements.md`, se compararon IMUs y microcontroladores con documentación oficial.

La selección se realizó contra los requisitos de:
- tres sensores simultáneos;
- orientación 3D identificable;
- timestamps y sincronización medibles;
- detección de datos inválidos/perdidos;
- acceso a datos inerciales para validación;
- compatibilidad con calibración sensor-segmento;
- logging;
- montaje wearable;
- validación cableada inicial;
- posibilidad de operación inalámbrica final.

Los límites numéricos de frecuencia, skew, latencia, error, drift y jitter permanecen PENDIENTES DE VALIDACIÓN.

## Decisión

### IMU
Adoptar **3 × STMicroelectronics ISM330BX**, una por segmento:
1. brazo;
2. antebrazo;
3. mano.

Razones principales:
- acelerómetro + giroscopio accesibles;
- algoritmo SFLP embebido capaz de generar Game Rotation Vector sin dependencia continua del magnetómetro;
- FIFO y timestamping del sensor;
- SPI;
- acceso a datos crudos para caracterización;
- documentación y driver oficial;
- permite validar el comportamiento real del sensor en D-006 sin cerrar la arquitectura a una única salida fusionada.

### MCU
Adoptar **Seeed Studio XIAO ESP32-S3 Plus** como MCU central del wearable.

Razones principales:
- un solo MCU puede concentrar la adquisición de las 3 IMUs;
- tamaño compacto de 21 × 17.8 mm;
- suficientes GPIO para el MVP y expansión;
- 2 SPI, 2 UART, I2C y USB;
- Wi-Fi 2.4 GHz y BLE 5.0 para evolución inalámbrica;
- recursos de cómputo/memoria muy superiores a los requeridos para adquisición, timestamping y empaquetado;
- disponibilidad de documentación, esquemático y archivos de diseño oficiales.

### Bus IMU → MCU
Adoptar **SPI compartido** para las tres IMUs, con **chip-select independiente por sensor**.

Arquitectura base:

```text
ISM330BX brazo ───── CS1 ┐
ISM330BX antebrazo ─ CS2 ├─ SPI compartido ─ XIAO ESP32-S3 Plus
ISM330BX mano ────── CS3 ┘
```

Las líneas de interrupción independientes permanecen PENDIENTES DE CIERRE DE PINOUT. Se utilizarán sólo si aportan valor medible a sincronización/adquisición.

### MCU → PC durante D-006
Adoptar **USB cableado** para la primera validación física.

Motivo:
reducir variables de latencia, pérdida de paquetes, alimentación y depuración mientras se caracteriza el wearable físico.

### Objetivo de comunicación final
La versión final del wearable deberá poder operar **sin cable de datos hacia la PC**.

El XIAO ESP32-S3 Plus preserva Wi-Fi y BLE como opciones.

**PENDIENTE DE DECISIÓN:** Wi-Fi vs BLE y protocolo/estructura de transporte final.

## Orientación y datos a transmitir

Como baseline de implementación:
- utilizar la salida de orientación SFLP del ISM330BX cuando sea útil;
- preservar acceso a acelerómetro y giroscopio crudos;
- convertir la orientación al contrato del pipeline: quaternion normalizado `[w,x,y,z]`;
- mantener `sensor_id`, timestamp y estado de validez;
- conservar logging suficiente para validar error, jitter/ruido, drift, sincronización, latencia y repetibilidad.

El uso del SFLP NO sustituye la validación física ni convierte sus especificaciones de datasheet en desempeño demostrado del wearable.

## Alternativas comparadas

### IMU
- **BNO085/BNO086:** técnicamente capaz, con sensor fusion y Game Rotation Vector; se descarta como primera opción por mayor riesgo/complexidad de integración de tres instancias y stack multi-sensor.
- **BHI385:** técnicamente potente, pero con complejidad de integración/alimentación no justificada para D-006.
- **BNO055:** no seleccionado; producto no recomendado para nuevos diseños por el fabricante.

### MCU
- **Raspberry Pi Pico 2 / Pico 2 W:** técnicamente suficiente y con más GPIO, pero el XIAO ESP32-S3 Plus ofrece un formato wearable más compacto y conserva Wi-Fi/BLE.
- **STM32G474:** excelente capacidad periférica, pero sobredimensionada para la función actual de adquisición.

## Fuente física de las IMUs

Se adopta el **chip ISM330BX**, pero todavía NO se adopta el carrier/breakout final de cada sensor.

Para prototipo inicial se evaluará el kit oficial **STEVAL-MKI245KA** frente a una carrier compacta apropiada.

La selección del carrier deberá considerar:
- tamaño y masa;
- montaje rígido al segmento;
- facilidad de cableado;
- acceso a SPI/INT;
- costo de tres unidades;
- disponibilidad;
- posibilidad de migrar posteriormente a PCB propia si se justifica.

## Alimentación

La arquitectura eléctrica definitiva permanece PENDIENTE.

La siguiente etapa deberá calcular:
- consumo máximo del XIAO ESP32-S3 Plus;
- consumo de 3 × ISM330BX;
- margen;
- alimentación por USB durante D-006;
- batería/regulación para modo inalámbrico final.

No se adopta batería ni regulador sin este cálculo.

## Pinout

El pinout definitivo permanece PENDIENTE.

Presupuesto conceptual:
- SCK, MOSI, MISO compartidos: 3 GPIO;
- CS por IMU: 3 GPIO;
- INT por IMU: hasta 3 GPIO adicionales;
- además deberá reservarse margen para clutch/recenter, gripper y háptica.

## Fuentes aceptadas asociadas

- **P-SEN-010 — STMicroelectronics, ISM330BX product documentation/datasheet.**
- **P-SEN-011 — Seeed Studio, XIAO ESP32-S3 Plus official documentation/datasheet.**
- **P-SEN-012 — Espressif Systems, ESP32-S3 Datasheet.**

Estas fuentes deben guardarse en NotebookLM de acuerdo con la regla de fuentes del proyecto.

## Relación con decisiones

- **D-002:** materializa la arquitectura de 3 IMUs.
- **D-006:** permite iniciar el wearable físico manteniendo la validación desacoplada del robot.
- **D-001:** no cambia; el mapping humano→robot sigue sin integrarse físicamente hasta cerrar D-006.

## Pendientes de validación

- carrier/breakout físico final del ISM330BX;
- pinout definitivo;
- alimentación y batería;
- frecuencia efectiva;
- skew entre sensores;
- latencia adquisición→PC;
- drift;
- jitter/ruido;
- error de orientación y reconstrucción;
- repetibilidad;
- Wi-Fi vs BLE;
- validación del enlace inalámbrico final.

## Criterio de revisión

D-007 deberá revisarse si las primeras pruebas físicas muestran que:
- el ISM330BX no satisface la estabilidad/precisión requerida;
- el XIAO ESP32-S3 Plus no ofrece recursos o GPIO suficientes;
- el SPI compartido no permite cumplir los requisitos temporales;
- la arquitectura inalámbrica final exige un cambio material de MCU.
