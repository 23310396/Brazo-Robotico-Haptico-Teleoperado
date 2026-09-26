# Plan de bring-up físico D-006

**Estado:** PLAN DE IMPLEMENTACIÓN — 25 de septiembre de 2026.  
**Área:** Wearable / Sensado / Firmware y validación inicial.  
**Trazabilidad:** D-002, D-006, D-007.

## Objetivo

Pasar de hardware recién recibido a adquisición física confiable sin mezclar simultáneamente todos los riesgos.

El orden obligatorio será:

```text
XIAO solo
  ↓
1 IMU por SPI
  ↓
1 IMU + INT1
  ↓
1 IMU + datos reales
  ↓
3 IMUs por SPI
  ↓
3 IMUs + INT1
  ↓
FIFO/timestamps
  ↓
USB → PC
  ↓
adaptador Python
  ↓
pipeline / logging
```

## F0 — XIAO solo

Antes de conectar una IMU:

- comprobar que el XIAO programa correctamente por USB;
- comprobar comunicación serial/USB con la PC;
- configurar el pinout D-006;
- dejar los tres CS en estado inactivo;
- comprobar que 3V3 está dentro del valor esperado con multímetro.

**Salida esperada:** MCU programable y comunicación PC estable.

## F1 — Una IMU, comunicación SPI mínima

Usar inicialmente el puerto asignado a BRAZO:

- SCK = D8;
- MISO = D9;
- MOSI = D10;
- CS = D0;
- INT1 = D4.

Conectar VDD y VDDIO a 3V3 y GND común.

Primera transacción:

```text
leer WHO_AM_I (registro 0x0F)
```

Según P-SEN-010, el ISM330BX devuelve:

```text
0x71
```

**Criterio F1:** lectura repetible de 0x71 sin errores de comunicación.

No avanzar a SFLP/FIFO antes de cerrar este punto.

## F2 — Una IMU, registros y datos crudos

Después de WHO_AM_I:

- reset/configuración documentada del sensor;
- configurar acelerómetro y giroscopio;
- leer accel/gyro;
- mover físicamente la placa y comprobar que las lecturas responden;
- registrar timestamp del MCU.

Los rangos y ODR iniciales todavía no se consideran criterios de aceptación físicos; serán parámetros de bring-up.

## F3 — Una IMU + INT1

Configurar INT1 y comprobar:

- evento real en D4;
- asociación evento → sensor brazo;
- contador de interrupciones;
- ausencia de interrupciones espurias evidentes.

Después se podrá decidir si INT1 representa data-ready, FIFO threshold u otro evento para la adquisición definitiva.

## F4 — Tres IMUs en banco

Agregar:

- antebrazo: CS D1 / INT1 D5;
- mano: CS D3 / INT1 D7.

Mantener SCK/MISO/MOSI comunes.

Comprobar individualmente WHO_AM_I=0x71 para cada CS.

**Criterio F4:** poder identificar y leer las tres IMUs de forma independiente sin que seleccionar una produzca respuestas de otra.

## F5 — Tres IMUs simultáneas

Ejecutar adquisición repetitiva y registrar:

- sensor_id;
- contador de secuencia;
- timestamp MCU;
- datos del sensor;
- flags de validez.

Comprobar:

- que no haya pérdida evidente de identificación;
- que las INT1 puedan distinguirse;
- frecuencia efectiva por sensor;
- errores SPI;
- paquetes perdidos/repetidos.

## F6 — FIFO, timestamp interno y SFLP

Sólo después de estabilizar SPI multi-IMU:

- habilitar FIFO;
- estudiar timestamp interno del ISM330BX;
- habilitar SFLP;
- extraer quaternion/Game Rotation Vector;
- preservar accel/gyro crudos para validación.

Este paso genera el dato que posteriormente se convertirá al contrato:

```text
sensor_id + timestamp + quaternion [w,x,y,z] + valid
```

## F7 — USB → PC

Transmitir primero un formato depurable y versionado.

Campos mínimos:

```text
sensor_id
seq
timestamp_mcu
timestamp_sensor   # si está disponible/validado
quaternion
valid
```

Durante bring-up pueden añadirse accel/gyro y flags de error.

El formato binario vs texto todavía está PENDIENTE DE DECISIÓN. Para depuración inicial se favorece legibilidad; para medición final se evaluará eficiencia/robustez.

## F8 — Python

Crear una capa de adquisición que convierta paquetes del MCU en los tipos que ya consume el pipeline.

El núcleo geométrico existente no deberá depender del puerto serial, USB, marca de IMU ni protocolo físico.

## Criterio de salida del bring-up

El hardware queda listo para pasar a calibración/reconstrucción cuando:

1. las tres IMUs sean identificables;
2. las tres entreguen datos reales;
3. timestamps y secuencias sean registrables;
4. la adquisición simultánea sea estable durante una sesión de prueba;
5. el PC pueda guardar los datos sin mezclar sensores;
6. se pueda alimentar el pipeline Python con esos datos.

Esto todavía NO cierra D-006; sólo cierra la adquisición física básica.
