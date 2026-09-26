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

**Extensión adoptada — 22 de septiembre de 2026:** utilizar SPI de **4 hilos**, con **CS independiente** e **INT1 independiente por cada IMU** durante D-006. Las tres IMUs compartirán SCK/MOSI/MISO.\n\n**Pinout adoptado — 25 de septiembre de 2026:** SCK=D8/GPIO7, MISO=D9/GPIO8, MOSI=D10/GPIO9; CS brazo=D0/GPIO1, CS antebrazo=D1/GPIO2, CS mano=D3/GPIO4; INT1 brazo=D4/GPIO5, INT1 antebrazo=D5/GPIO6 e INT1 mano=D7/GPIO44. D2/GPIO3 queda fuera del arnés y D6/GPIO43 se reserva para depuración TX0.

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

Se adopta el **chip ISM330BX**.

**Extensión adoptada — 22 de septiembre de 2026:** para la primera validación física de D-006 se utilizarán **3 × STEVAL-MKI245KA**, uno por segmento. Esta selección aplica al prototipo/validación; el carrier final de la manga permanece PENDIENTE y podrá sustituirse por una solución más compacta después de validar el sensor.

La selección del carrier deberá considerar:
- tamaño y masa;
- montaje rígido al segmento;
- facilidad de cableado;
- acceso a SPI/INT;
- costo de tres unidades;
- disponibilidad;
- posibilidad de migrar posteriormente a PCB propia si se justifica.

## Alimentación

**Extensión adoptada — 22 de septiembre de 2026:** durante D-006 el XIAO ESP32-S3 Plus se alimentará desde USB y las tres IMUs se alimentarán a **3.3 V desde el XIAO**, dentro de los rangos documentados del ISM330BX.

La batería y la regulación para el modo inalámbrico final permanecen PENDIENTES. No se adopta capacidad de batería ni regulador sin cerrar el protocolo inalámbrico, duración objetivo de sesión y consumo real del sistema completo.

## Pinout

El **mapeo exacto de GPIO** permanece PENDIENTE.

Arquitectura de señales adoptada:
- SCK, MOSI y MISO compartidos: 3 GPIO;
- CS por IMU: 3 GPIO;
- INT1 por IMU: 3 GPIO;
- reservar margen para clutch/recenter, gripper y háptica.

La velocidad de SPI permanecerá configurable y se determinará experimentalmente para evitar asumir que la frecuencia máxima del sensor es apropiada para el arnés wearable.

## Fuentes aceptadas asociadas

- **P-SEN-010 — STMicroelectronics, ISM330BX product documentation/datasheet.**
- **P-SEN-011 — Seeed Studio, XIAO ESP32-S3 Plus official documentation/datasheet.**
- **P-SEN-012 — Espressif Systems, ESP32-S3 Datasheet.**
- **P-SEN-013 — STMicroelectronics, STEVAL-MKI245KA product/data brief and official design resources.**

Estas fuentes deben guardarse en NotebookLM de acuerdo con la regla de fuentes del proyecto.

## Relación con decisiones

- **D-002:** materializa la arquitectura de 3 IMUs.
- **D-006:** permite iniciar el wearable físico manteniendo la validación desacoplada del robot.
- **D-001:** no cambia; el mapping humano→robot sigue sin integrarse físicamente hasta cerrar D-006.

## Pendientes de validación

- carrier/breakout físico de la versión final (D-006 usa STEVAL-MKI245KA);
- mapeo exacto de GPIO;
- velocidad SPI validada sobre el arnés;
- batería/regulación para modo inalámbrico final;
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


## BOM y costo de referencia

Los costos vigentes y rubros pendientes se mantienen en `hardware/BOM.md`. El precio de compra no sustituye los criterios técnicos de esta decisión y deberá actualizarse al realizar la compra.
