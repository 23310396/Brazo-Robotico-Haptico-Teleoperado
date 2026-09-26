# Pinout de adquisición D-006

**Estado:** DECISIÓN DE IMPLEMENTACIÓN — aprobada por el equipo el 25 de septiembre de 2026.  
**Área:** Wearable / Sensado / Hardware de adquisición.  
**Trazabilidad:** D-002, D-006, D-007; P-SEN-010, P-SEN-011, P-SEN-012, P-SEN-013.

## Objetivo

Cerrar el mapeo físico entre el Seeed Studio XIAO ESP32-S3 Plus y las 3 × STEVAL-MKI245KA usadas para la primera validación D-006.

La arquitectura adoptada permanece:

```text
3 × ISM330BX
  ├─ SCK compartido
  ├─ MOSI compartido
  ├─ MISO compartido
  ├─ CS independiente
  └─ INT1 independiente
          ↓
XIAO ESP32-S3 Plus
          ↓
USB
          ↓
PC
```

## Evidencia de las fuentes aceptadas

### P-SEN-011 — XIAO ESP32-S3 Plus

La documentación oficial de Seeed asigna:

- D8 = GPIO7 = SCK;
- D9 = GPIO8 = MISO;
- D10 = GPIO9 = MOSI;
- D0 = GPIO1;
- D1 = GPIO2;
- D2 = GPIO3;
- D3 = GPIO4;
- D4 = GPIO5;
- D5 = GPIO6;
- D6 = GPIO43 / TX;
- D7 = GPIO44 / RX.

### P-SEN-012 — ESP32-S3

La documentación oficial de Espressif identifica:

- GPIO3 como pin de strapping;
- GPIO43 y GPIO44 como interfaz UART0;
- GPIO19 y GPIO20 como USB Serial/JTAG.

Por robustez de arranque se adopta no usar D2/GPIO3 en el arnés de las IMUs.  
Se conserva D6/GPIO43 (TX0) libre para depuración de emergencia.  
D7/GPIO44 se utilizará como entrada de interrupción; esto sacrifica RX0 para D-006, pero no interfiere con el USB adoptado.

### P-SEN-010 — ISM330BX

En SPI de 4 hilos:

- SCL del ISM330BX funciona como SPC/SCK;
- SDA funciona como SDI/MOSI;
- SDO/SA0 funciona como SDO/MISO;
- CS selecciona cada dispositivo;
- INT1 es una salida de interrupción programable.

El datasheet caracteriza SPI hasta 10 MHz. Ese valor es un máximo del dispositivo, **no** la velocidad adoptada para el arnés.

### P-SEN-013 — STEVAL-MKI245KA

El carrier oficial expone el pinout del ISM330BX y contiene el desacoplo requerido para VDD y VDDIO. Para D-006 se conectarán las señales por nombre de red del carrier: VDD, VDDIO, GND, SCL, SDA, SDO/SA0, CS e INT1.

## Pinout adoptado del XIAO

| Función | XIAO | GPIO ESP32-S3 | Dirección MCU | Destino |
|---|---|---:|---|---|
| SPI SCK compartido | D8 | GPIO7 | salida | SCL/SPC de las 3 IMUs |
| SPI MISO compartido | D9 | GPIO8 | entrada | SDO/SA0 de las 3 IMUs |
| SPI MOSI compartido | D10 | GPIO9 | salida | SDA/SDI de las 3 IMUs |
| CS brazo | D0 | GPIO1 | salida | CS IMU brazo |
| CS antebrazo | D1 | GPIO2 | salida | CS IMU antebrazo |
| CS mano | D3 | GPIO4 | salida | CS IMU mano |
| INT1 brazo | D4 | GPIO5 | entrada | INT1 IMU brazo |
| INT1 antebrazo | D5 | GPIO6 | entrada | INT1 IMU antebrazo |
| INT1 mano | D7 | GPIO44 | entrada | INT1 IMU mano |
| Alimentación | 3V3 | — | salida alimentación | VDD + VDDIO de las 3 IMUs |
| Referencia | GND | — | — | GND común |

## Pines deliberadamente reservados

| XIAO | GPIO | Estado | Razón |
|---|---:|---|---|
| D2 | GPIO3 | NO USAR en D-006 | pin de strapping del ESP32-S3 |
| D6 | GPIO43 | RESERVAR | TX0 / depuración de emergencia |
| D11–D19 | varios | RESERVA | expansión futura sin depender de ellos para el primer arnés |

## Topología eléctrica de señales

```text
XIAO D8  / GPIO7  ───── SCK ─────┬─ IMU brazo SCL/SPC
                                  ├─ IMU antebrazo SCL/SPC
                                  └─ IMU mano SCL/SPC

XIAO D10 / GPIO9  ───── MOSI ─────┬─ IMU brazo SDA/SDI
                                   ├─ IMU antebrazo SDA/SDI
                                   └─ IMU mano SDA/SDI

XIAO D9  / GPIO8  ───── MISO ─────┬─ IMU brazo SDO/SA0
                                   ├─ IMU antebrazo SDO/SA0
                                   └─ IMU mano SDO/SA0

D0 ─ CS brazo
D1 ─ CS antebrazo
D3 ─ CS mano

D4 ← INT1 brazo
D5 ← INT1 antebrazo
D7 ← INT1 mano

3V3 ─ VDD + VDDIO de las tres placas
GND ─ GND común
```

## Reglas de firmware derivadas

1. configurar los tres CS como salida y mantenerlos en nivel inactivo antes de iniciar transacciones;
2. seleccionar únicamente una IMU a la vez;
3. configurar INT1 de cada IMU en un GPIO independiente;
4. registrar qué INT disparó y asociarlo al sensor correspondiente;
5. mantener la velocidad SPI configurable;
6. no adoptar todavía 10 MHz como velocidad operativa;
7. validar físicamente la integridad del bus con el arnés real antes de incrementar la velocidad.

## Pendientes posteriores al cierre del pinout

1. definir ubicación física del XIAO;
2. definir topología, longitud aproximada y conectores del arnés;
3. verificar en las placas físicas qué cabecera del STEVAL-MKIGI06A se utilizará para cada señal;
4. implementar firmware mínimo de bring-up con **1 IMU**;
5. validar identificación/WHO_AM_I y lectura por SPI;
6. extender posteriormente a 3 IMUs + INT1 + FIFO/timestamps.
