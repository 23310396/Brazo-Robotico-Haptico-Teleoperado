# Plan de compras D-006 — wearable

**Estado:** PLAN OPERATIVO — 25 de septiembre de 2026.  
**Trazabilidad:** D-002, D-006, D-007, `hardware/BOM.md`.

## Compra inmediata — no requiere cerrar el arnés final

### Hardware principal adoptado

| Componente | Cantidad | Identificador exacto | Estado |
|---|---:|---|---|
| STMicroelectronics STEVAL-MKI245KA | 3 | STEVAL-MKI245KA | COMPRAR YA |
| Seeed Studio XIAO ESP32-S3 Plus | 1 | SKU 102010671 | COMPRAR YA |

Para el XIAO se prefiere la variante con headers pre-soldados si está disponible, porque facilita el bring-up en protoboard.

### Consumibles de banco

Comprar sólo si no están ya disponibles:

- 1 protoboard;
- jumpers Dupont macho-macho y macho-hembra;
- 1 cable USB-C de **datos**, no sólo carga;
- multímetro disponible para verificar 3.3 V/GND antes de energizar sensores.

Estos consumibles no forman parte de la arquitectura final.

## NO comprar todavía

Hasta validar 1 IMU y luego 3 IMUs en banco:

- conectores JST-PH7;
- cable AWG28 para arnés corporal;
- placa/hub definitivo;
- soportes/manga;
- batería/regulador;
- hardware Wi-Fi/BLE adicional;
- carrier compacto final del ISM330BX.

Motivo: longitud del arnés, ubicación final del MCU y detalles de retención se medirán/validarán sobre el prototipo físico.

## Compra posterior — después de 3 IMUs estables en banco

Una vez confirmados:

1. SPI de una IMU;
2. WHO_AM_I;
3. INT1;
4. tres CS independientes;
5. tres INT1;
6. funcionamiento simultáneo del bus;

se medirán físicamente las rutas del wearable y se cerrará:

- conector del arnés;
- calibre/tipo de cable;
- longitud de los tres ramales;
- hub soldado/PCB;
- alivio de tensión;
- fijación temporal del MCU y adaptadores.

## Búsquedas exactas recomendadas

### IMU

Buscar literalmente:

```text
STEVAL-MKI245KA
```

Verificar antes de comprar:
- fabricante: STMicroelectronics;
- kit basado en ISM330BX;
- que el código termine exactamente en `245KA`, no `244A` ni otro STEVAL.

### MCU

Buscar literalmente:

```text
Seeed Studio XIAO ESP32-S3 Plus 102010671
```

Verificar:
- que diga **Plus**;
- SKU `102010671`;
- no comprar por error XIAO ESP32-S3 normal, Sense, C3, C6 u otra variante.

## Regla de compra

No sustituir una pieza por una “equivalente” sin regresar a 01/02 para revisar impacto técnico.
