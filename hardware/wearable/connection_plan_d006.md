# Plan de conexión física D-006 — wearable

**Estado:** PROPUESTA TÉCNICA — pendiente de aprobación.  
**Área:** Wearable / Sensado / Arnés y conexión física.  
**Trazabilidad:** D-002, D-006, D-007; P-SEN-010, P-SEN-011, P-SEN-013.

## 1. Objetivo

Definir cómo pasar del pinout eléctrico ya adoptado a una conexión física que pueda:

- probar primero 1 IMU en banco;
- escalar después a 3 IMUs;
- desmontarse por sensor;
- permitir depuración;
- montarse temporalmente sobre el brazo para D-006;
- mantener accesibles las señales necesarias para sincronización y logging.

No define todavía el conector final ni la manga definitiva.

## 2. Particularidad del STEVAL-MKI245KA

Cada STEVAL-MKI245KA está compuesto por:

1. una PCB pequeña con el ISM330BX;
2. un cable plano;
3. la placa adaptadora STEVAL-MKIGI06A.

La documentación oficial del kit indica un cable plano de aproximadamente 30 cm entre la PCB del sensor y el adaptador.

**Consecuencia de diseño:** para D-006 se propone montar únicamente la PCB pequeña del sensor sobre el segmento corporal y dejar la placa adaptadora en una zona donde pueda conectarse al arnés. La placa adaptadora no debe confundirse con la IMU que necesita quedar rígida respecto al segmento.

## 3. Arquitectura física propuesta

Para la primera validación se propone una topología de **estrella** desde un pequeño hub junto al XIAO:

```text
                         ┌─ ramal 7 hilos → adaptador IMU brazo → cable plano → sensor brazo
PC ─ USB ─ XIAO + HUB ──┼─ ramal 7 hilos → adaptador IMU antebrazo → cable plano → sensor antebrazo
                         └─ ramal 7 hilos → adaptador IMU mano → cable plano → sensor mano
```

Aunque físicamente existan tres ramales, SCK/MOSI/MISO/3V3/GND continúan siendo eléctricamente compartidos en el hub.

## 4. Señales de cada ramal

Cada ramal tendrá conceptualmente 7 conductores:

| # | Señal | Tipo | Compartida/individual |
|---|---|---|---|
| 1 | 3V3 | alimentación | compartida |
| 2 | GND | referencia | compartida |
| 3 | SCK | SPI | compartida |
| 4 | MOSI | SPI | compartida |
| 5 | MISO | SPI | compartida |
| 6 | CS_i | SPI | individual |
| 7 | INT1_i | interrupción | individual |

En la placa adaptadora, el conductor 3V3 deberá alimentar tanto VDD como VDDIO.

No se utilizarán durante D-006:

- INT2;
- TDM;
- BCLK;
- WCLK;
- señales QVAR.

## 5. Hub junto al XIAO

**PROPUESTA:** no unir tres cables directamente dentro de un mismo pin del XIAO.

Se utilizará un pequeño punto de distribución donde:

- D8/SCK se divida en tres;
- D10/MOSI se divida en tres;
- D9/MISO conecte los tres retornos;
- 3V3 se distribuya a los tres ramales;
- GND se distribuya a los tres ramales;
- los 3 CS permanezcan separados;
- los 3 INT1 permanezcan separados.

Para pruebas de banco puede implementarse temporalmente en breadboard/protoboard.

Para colocar el sistema sobre el cuerpo, deberá migrarse a una unión soldada o placa perforada/PCB de distribución; no se considera adecuado depender de un breadboard móvil.

## 6. Conectividad por etapas

### Etapa A — bring-up de banco, 1 IMU

```text
PC ─ USB ─ XIAO ─ SPI ─ STEVAL-MKIGI06A ─ cable plano ─ ISM330BX
```

Objetivo:

- comprobar alimentación;
- leer WHO_AM_I;
- leer/escribir registros por SPI;
- verificar INT1;
- comprobar que no existen errores de cableado.

En esta etapa se permiten jumpers/Dupont como medio temporal de laboratorio.

### Etapa B — banco, 3 IMUs

Agregar los tres ramales y comprobar:

- CS individual;
- identificación inequívoca de cada sensor;
- bus SPI compartido;
- las tres INT1;
- ausencia de contención MISO;
- funcionamiento simultáneo antes de montar nada sobre el cuerpo.

### Etapa C — arnés corporal D-006

Sustituir las conexiones temporales por un arnés desmontable y con retención mecánica.

**Requisito del conector:** cada ramal debe usar un conector polarizado/bloqueable de al menos 7 contactos o una solución equivalente que evite invertir el cableado.

El modelo comercial de conector permanece **PENDIENTE DE SELECCIÓN**.

## 7. Ubicación del MCU

### PROPUESTA PRINCIPAL

Colocar el XIAO + hub en el **brazo superior, en una zona proximal/lateral**, dentro de un pequeño módulo separado del sensor.

Razones:

- mantiene masa/electrónica lejos de mano y muñeca;
- permite dirigir el cable USB hacia torso/PC sin que salga desde la mano;
- deja libres muñeca y mano para validar orientación;
- concentra la distribución del arnés;
- el XIAO es suficientemente pequeño para este montaje.

### Riesgo

Los ramales hacia antebrazo/mano serán los más largos. Por ello:

- no se fija todavía velocidad SPI alta;
- longitud exacta se medirá sobre el operador;
- la velocidad SPI se validará físicamente con el arnés real.

Esta ubicación permanece **PROPUESTA** hasta probar comodidad y longitudes reales.

## 8. Ruta del arnés

**PROPUESTA:**

- cableado por el lado externo/lateral del miembro superior;
- sujetar el arnés a intervalos para que el peso del cable no jale las IMUs;
- dejar holgura controlada cerca de codo y muñeca;
- evitar que una flexión completa tense el cable;
- separar la función de soporte del cable de la fijación rígida de cada IMU.

La longitud exacta de cada ramal está **PENDIENTE DE MEDICIÓN FÍSICA**.

## 9. Protección contra errores de montaje

Cada ramal deberá identificarse visualmente y en firmware:

- BRAZO;
- ANTEBRAZO;
- MANO.

Se recomienda que el conector/harness tenga etiqueta permanente y que el firmware mantenga la misma asociación:

```text
CS brazo       = D0
INT1 brazo     = D4

CS antebrazo   = D1
INT1 antebrazo = D5

CS mano        = D3
INT1 mano      = D7
```

No confiar únicamente en el orden físico de los cables.

## 10. Secuencia de armado propuesta

1. montar XIAO en banco;
2. crear un único ramal de prueba;
3. conectar una STEVAL-MKI245KA;
4. verificar 3V3/GND antes de comunicación;
5. ejecutar bring-up SPI y WHO_AM_I;
6. validar INT1;
7. replicar el ramal para la segunda y tercera IMU;
8. probar 3 sensores simultáneos en banco;
9. medir las rutas reales sobre el operador;
10. seleccionar conectores y cableado del arnés corporal;
11. construir el arnés D-006;
12. montar sensores sobre brazo, antebrazo y mano;
13. empezar validación física de adquisición/sincronización.

## 11. Decisiones todavía NO tomadas

- conector comercial del arnés;
- calibre/tipo exacto de cable;
- longitud de cada ramal;
- ubicación definitiva del XIAO;
- soporte mecánico del XIAO;
- soporte definitivo de las IMUs;
- velocidad SPI;
- batería;
- Wi-Fi vs BLE;
- carrier final de producto.

## 12. Puerta al firmware

Una vez aprobada esta topología, el siguiente incremento de 02 será el **firmware mínimo de bring-up de una sola ISM330BX**, todavía sin intentar ejecutar las tres IMUs ni SFLP/FIFO de golpe.
