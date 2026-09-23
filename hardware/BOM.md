# BOM preliminar — Brazo Robótico Háptico Teleoperado

**Última actualización:** 22 de septiembre de 2026  
**Estado:** PRELIMINAR — sólo incluye componentes ya seleccionados o rubros explícitamente pendientes.  
**Moneda de referencia:** USD y MXN.

> Este BOM no representa todavía el costo total final del proyecto. Los costos de robot, gripper, fuerza, háptica, batería, cableado, soportes y fabricación se incorporarán cuando exista selección técnica.

## Wearable — adquisición D-006 / D-007

| Componente | Cant. | Estado | Precio unitario ref. | Subtotal USD | Subtotal MXN aprox. |
|---|---:|---|---:|---:|---:|
| ST STEVAL-MKI245KA (ISM330BX) | 3 | ADOPTADO para primera validación D-006 | US$33.10 (DigiKey) | US$99.30 | $1,720.33 |
| Seeed Studio XIAO ESP32-S3 Plus | 1 | ADOPTADO | US$7.99 (Seeed Studio) | US$7.99 | $138.41 |
| **Subtotal hardware de adquisición seleccionado** |  |  |  | **US$107.29** | **$1,858.64** |

**Tipo de cambio de referencia:** 1 USD = 17.3235 MXN (consulta 22/23-sep-2026).  
**No incluidos:** envío, impuestos/importación, cableado, conectores, manga/soportes ni consumibles.

## Pendientes del wearable

| Rubro | Estado de costo |
|---|---|
| Cableado/conectores del arnés SPI | PENDIENTE DE DISEÑO/SELECCIÓN |
| Manga/correas/soportes | PENDIENTE DE DISEÑO |
| Batería y regulación para modo inalámbrico | PENDIENTE de Wi-Fi vs BLE, duración objetivo y medición de consumo |
| Carrier IMU de versión final | PENDIENTE; D-006 usa STEVAL-MKI245KA |
| Clutch/recenter | PENDIENTE DE IMPLEMENTACIÓN |
| Sensor/mecanismo de apertura-cierre | PENDIENTE DE SELECCIÓN |
| Hardware háptico | PENDIENTE — D-004 define modalidad, no componente |
| Sensado de fuerza | PENDIENTE — D-003 define principio, no componente |

## Otros subsistemas del proyecto

Los rubros de manipulador 6R, actuadores/transmisiones, gripper, fuerza, háptica, control convencional y fabricación siguen sin BOM comercial cerrado. No deben presentarse como costos exactos hasta completar sus selecciones.

El Contexto Maestro mantiene un presupuesto global preliminar como referencia de planeación, pero deberá actualizarse progresivamente con este BOM real.

## Fuentes de precio

- STEVAL-MKI245KA: DigiKey, referencia 497-STEVAL-MKI245KA-ND, precio unitario consultado US$33.10.
- XIAO ESP32-S3 Plus: Seeed Studio, SKU 102010671, precio consultado US$7.99.
- Tipo de cambio: 1 USD = 17.3235 MXN, consulta 22/23-sep-2026.

## Trazabilidad

- D-002 — captura con 3 IMUs.
- D-006 — validar wearable antes de integrar robot.
- D-007 — ISM330BX + XIAO ESP32-S3 Plus + SPI.
- P-SEN-010 — ISM330BX.
- P-SEN-011 — XIAO ESP32-S3 Plus.
- P-SEN-012 — ESP32-S3.
- P-SEN-013 — STEVAL-MKI245KA.
