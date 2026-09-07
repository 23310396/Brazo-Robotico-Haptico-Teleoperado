# Requisitos de adquisición del wearable

Documento de transición entre la validación sintética del pipeline y la selección de hardware real.

Su objetivo es responder: **¿qué debe entregar físicamente el sistema de 3 IMUs para que el pipeline de pose pueda operar y D-006 pueda validarse con hardware real?**

No selecciona todavía una IMU ni un microcontrolador comercial.

## Trazabilidad

- **D-002 — DECISIÓN:** captura del operador con 3 IMUs: brazo, antebrazo y mano.
- **D-006 — DECISIÓN:** validar el wearable como subsistema independiente antes de integrar el robot.
- **IMPLEMENTADO:** el pipeline Python recibe tres orientaciones, timestamps, identificadores y estado de validez, aplica calibración conocida y reconstruye codo, muñeca y orientación de mano.
- **IMPLEMENTADO:** la caracterización sintética cubre error angular, calibración residual, ruido/jitter, drift, desincronización dinámica, rotaciones 3D y error en longitudes de segmentos.

## Contrato mínimo de cada muestra

El pipeline actual utiliza conceptualmente:

```text
sensor_id
+
timestamp
+
orientación quaternion [w, x, y, z]
+
estado de validez
```

El hardware real podrá entregar información adicional, pero no deberá perder estos campos al llegar al software de reconstrucción.

---

## Requisitos de adquisición

### R-WEA-ACQ-001 — Tres canales de orientación

**DECISIÓN / REQUISITO**

El sistema deberá adquirir de forma continua tres orientaciones asociadas inequívocamente a:

1. brazo;
2. antebrazo;
3. mano.

No se requiere una IMU adicional en torso mientras se mantenga la hipótesis vigente de torso aproximadamente fijo.

### R-WEA-ACQ-002 — Orientación tridimensional

**REQUISITO**

Cada canal deberá proporcionar una orientación 3D que pueda expresarse como quaternion normalizado `[w, x, y, z]` en una convención de frames conocida y documentada.

La orientación puede provenir directamente de la IMU o calcularse antes de entrar al pipeline, pero la convención utilizada deberá poder verificarse experimentalmente.

### R-WEA-ACQ-003 — Identificación inequívoca de sensores

**REQUISITO**

Cada muestra deberá mantener un identificador estable de sensor/segmento para evitar intercambiar brazo, antebrazo y mano por errores de orden o comunicación.

### R-WEA-ACQ-004 — Timestamp cercano a la adquisición

**REQUISITO**

Cada muestra deberá llevar un timestamp generado lo más cerca posible del instante real de adquisición, no únicamente en el momento en que el paquete llega a la PC.

Los tres sensores deberán usar una base temporal común o un mecanismo que permita convertir sus timestamps a una base común.

### R-WEA-ACQ-005 — Sincronización medible

**REQUISITO**

El sistema deberá permitir calcular el skew temporal entre las tres muestras utilizadas para una reconstrucción:

```text
skew = max(timestamp) - min(timestamp)
```

El valor máximo aceptable de skew permanece **PENDIENTE DE VALIDACIÓN**.

La simulación de desincronización demostró que el mismo skew puede producir distinto error dependiendo de la velocidad de movimiento, por lo que no se adoptará un límite temporal arbitrario.

Relación aproximada útil para una orientación individual:

```text
error_angular_temporal ≈ velocidad_angular * desfase_temporal
```

Por tanto, cuando se defina el error angular temporal permitido `e_theta_max` y la velocidad angular de diseño `omega_max`, podrá estimarse:

```text
Delta_t_max <= e_theta_max / omega_max
```

### R-WEA-ACQ-006 — Frecuencia de actualización conocida y estable

**REQUISITO**

La frecuencia efectiva de actualización de cada sensor deberá ser conocida, medible y suficientemente estable para reconstrucción y visualización en tiempo real.

El valor mínimo `f_sample_min` está **PENDIENTE DE DEFINICIÓN**.

No se fijará sólo por disponibilidad comercial. Deberá relacionarse con la velocidad de movimiento que se quiera representar y el cambio angular máximo admisible entre muestras. Como referencia de diseño:

```text
Delta_theta_por_muestra ≈ omega / f_sample
```

### R-WEA-ACQ-007 — Latencia medible separada del skew

**REQUISITO**

La arquitectura deberá permitir medir la latencia entre adquisición y disponibilidad de la muestra en la PC.

La latencia común no deberá confundirse con la desincronización entre sensores: tres sensores pueden tener skew interno cercano a cero y aun así representar una pose atrasada.

El límite de latencia aceptable permanece **PENDIENTE DE VALIDACIÓN**.

### R-WEA-ACQ-008 — Detección de muestra inválida, perdida o vieja

**REQUISITO**

El sistema deberá poder distinguir una muestra válida de una muestra ausente, corrupta o demasiado antigua.

La implementación de firmware deberá permitir detectar pérdidas o saltos de datos; un contador de secuencia por paquete es una **PROPUESTA** para este fin.

No se deberá fabricar silenciosamente una orientación válida cuando el dato real no esté disponible.

### R-WEA-ACQ-009 — Acceso a datos inerciales crudos

**PROPUESTA FUERTE — CRITERIO DE SELECCIÓN**

Se prefiere que cada IMU permita acceder, además de una posible orientación fusionada, a:

- acelerómetro;
- giroscopio;
- magnetómetro, si existe.

Esto permitiría caracterizar ruido, verificar la fusión del fabricante y, si fuera necesario, implementar o comparar un algoritmo de fusión propio.

No es todavía requisito obligatorio de compra hasta comparar alternativas y complejidad en 01.

### R-WEA-ACQ-010 — No dependencia obligatoria del magnetómetro continuo

**DECISIÓN / REQUISITO DE ARQUITECTURA**

La operación base del wearable no deberá depender ciegamente de un magnetómetro continuamente confiable.

Si el hardware seleccionado incluye magnetómetro, su uso deberá poder evaluarse, habilitarse o deshabilitarse de manera explícita. La estrategia final de heading/recenter sigue pendiente.

### R-WEA-ACQ-011 — Compatibilidad con calibración sensor-segmento

**REQUISITO**

Cada IMU deberá permanecer montada rígidamente respecto al segmento corporal durante una sesión.

El software deberá poder conservar una transformación de calibración independiente por sensor `q_S_B` y una relación de frame de navegación/humano `q_H_N`.

No es requisito que las tres placas queden físicamente instaladas con exactamente la misma orientación; la calibración deberá representar sus offsets reales.

### R-WEA-ACQ-012 — Longitudes de brazo y antebrazo configurables

**REQUISITO**

El sistema deberá aceptar longitudes individuales de:

```text
L_brazo
L_antebrazo
```

porque la reconstrucción cartesiana depende directamente de ellas.

El procedimiento físico de medición y la incertidumbre máxima permisible están **PENDIENTES DE DEFINICIÓN/VALIDACIÓN**.

### R-WEA-ACQ-013 — Capacidad real para tres sensores simultáneos

**REQUISITO DE SELECCIÓN DE HARDWARE**

La combinación IMU + MCU deberá permitir operar tres unidades simultáneamente sin conflictos irresolubles de dirección, bus o ancho de banda.

Durante la comparación deberán revisarse explícitamente:

- I2C/SPI/UART u otras interfaces disponibles;
- direcciones configurables;
- chip-select si aplica;
- FIFO/interrupciones si existen;
- tasa de datos máxima del bus;
- soporte real para tres dispositivos.

### R-WEA-ACQ-014 — Comunicación MCU → PC trazable

**REQUISITO**

La comunicación hacia la PC deberá preservar como mínimo:

```text
sensor_id + timestamp + quaternion + valid
```

La interfaz física definitiva permanece **PENDIENTE DE DECISIÓN**.

**PROPUESTA MVP:** comenzar con enlace cableado por USB/serial para reducir variables de latencia, pérdida de paquetes y alimentación durante la primera validación física. Una solución inalámbrica sólo se adoptará si aporta valor suficiente al experimento.

### R-WEA-ACQ-015 — Registro de datos para validación

**REQUISITO derivado de D-006**

El sistema deberá poder guardar sesiones con los datos necesarios para calcular posteriormente:

- error;
- estabilidad;
- jitter/ruido;
- drift;
- sincronización;
- latencia cuando sea medible;
- repetibilidad.

Como mínimo deberán registrarse las orientaciones y timestamps usados por el pipeline. Si están disponibles datos crudos, también deberán poder registrarse.

### R-WEA-ACQ-016 — Visualización en tiempo real desacoplada del hardware

**REQUISITO FUNCIONAL**

La adquisición física deberá alimentar el mismo contrato software usado por los datos sintéticos para que el visualizador no dependa de una marca concreta de IMU.

La meta de D-006 permanece:

```text
IMUs reales -> adquisición -> calibración -> reconstrucción -> visualización en tiempo real
```

### R-WEA-ACQ-017 — Alimentación compatible y estable

**REQUISITO DE SELECCIÓN**

La arquitectura deberá alimentar simultáneamente el MCU y las tres IMUs dentro de sus rangos documentados, sin introducir reinicios o comportamiento inestable.

El presupuesto de corriente y la fuente definitiva se calcularán después de seleccionar componentes.

### R-WEA-ACQ-018 — Montaje mecánico estable

**REQUISITO**

Cada sensor deberá poder fijarse al segmento corporal de manera que el movimiento relativo sensor-piel/segmento sea suficientemente pequeño y repetible durante una sesión.

Tamaño, masa, rigidez de soporte y método de fijación serán criterios de selección/diseño físico. Sus límites numéricos están **PENDIENTES DE VALIDACIÓN**.

---

## Parámetros numéricos aún pendientes

No deben confundirse con requisitos omitidos. Son variables que deben cerrarse con evidencia antes de la validación física final:

| Parámetro | Estado |
|---|---|
| Error angular máximo aceptable | PENDIENTE DE VALIDACIÓN |
| Error de posición de muñeca aceptable | PENDIENTE DE VALIDACIÓN |
| Frecuencia mínima de actualización | PENDIENTE DE DEFINICIÓN |
| Skew máximo entre sensores | PENDIENTE DE DEFINICIÓN/VALIDACIÓN |
| Latencia máxima adquisición→PC | PENDIENTE DE DEFINICIÓN/VALIDACIÓN |
| Drift máximo durante una sesión | PENDIENTE DE VALIDACIÓN |
| Ruido/jitter máximo | PENDIENTE DE VALIDACIÓN |
| Incertidumbre máxima en longitudes corporales | PENDIENTE DE VALIDACIÓN |
| Duración objetivo de una sesión | PENDIENTE DE DEFINICIÓN |
| Masa/tamaño máximo por módulo | PENDIENTE DE DISEÑO FÍSICO |
| Consumo/presupuesto de energía | PENDIENTE DE SELECCIÓN DE HARDWARE |

## Puerta para iniciar selección de hardware

Con estos requisitos puede comenzar la búsqueda de IMUs y MCU sin haber elegido aún valores arbitrarios para todos los umbrales físicos.

La selección deberá distinguir:

1. **cumplimiento obligatorio:** 3 sensores, orientación 3D, identificación, timestamps/sincronización medible, compatibilidad de bus, calibración, logging y alimentación;
2. **criterios comparativos:** tasa máxima, calidad de orientación, acceso a datos crudos, FIFO, tamaño, consumo, costo, disponibilidad y calidad de documentación;
3. **pendientes experimentales:** error real, drift real, jitter real, latencia real, repetibilidad y comportamiento del montaje físico.

Si una alternativa no permite verificar o medir variables necesarias para D-006, deberá descartarse aunque sea barata o popular.

## Siguiente paso

**CAMBIO DE CHAT previsto → 01 — Investigación y decisiones**

Usar este documento como entrada para comparar IMUs y microcontroladores mediante datasheets/documentación oficial. No adoptar componentes hasta documentar alternativas, evidencia, limitaciones e impacto en firmware/mecánica/validación.
