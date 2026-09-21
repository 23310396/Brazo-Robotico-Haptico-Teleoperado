# Fuentes aceptadas — selección de hardware wearable

Fecha de aceptación: **20 de septiembre de 2026**

Este archivo registra las fuentes primarias aceptadas para D-007.

## P-SEN-010 — ISM330BX

- **ID:** P-SEN-010
- **Autor/organización:** STMicroelectronics
- **Título:** ISM330BX — 6-axis IMU with wide bandwidth, low-noise accelerometer, embedded AI and sensor fusion for industrial applications
- **Tipo:** Datasheet / documentación oficial de producto
- **URL:** https://www.st.com/en/mems-and-sensors/ism330bx.html
- **Área principal:** Wearable / Sensado
- **Áreas secundarias:** IMU; sensor fusion; adquisición; SPI; timing
- **Estado:** ACEPTADA
- **Motivo de inclusión:** fuente primaria para capacidades, interfaces, alimentación, FIFO, SFLP, timestamping y características del ISM330BX.
- **Aplicación:** D-007; selección de IMU; firmware; validación D-006.
- **NotebookLM:** REGISTRO/ALMACENAMIENTO OBLIGATORIO — sección Wearable/Sensado → Hardware/IMU.

## P-SEN-011 — XIAO ESP32-S3 Plus

- **ID:** P-SEN-011
- **Autor/organización:** Seeed Studio
- **Título:** Seeed Studio XIAO ESP32-S3 Plus — official documentation / industrial product datasheet
- **Tipo:** Datasheet / documentación oficial de placa
- **URL:** https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/
- **Área principal:** Wearable / Sensado
- **Áreas secundarias:** MCU; electrónica; comunicaciones; wearable hardware
- **Estado:** ACEPTADA
- **Motivo de inclusión:** fuente primaria para pinout, interfaces, dimensiones, memoria, wireless y recursos de la placa adoptada.
- **Aplicación:** D-007; MCU central; pinout; USB; futura operación inalámbrica.
- **NotebookLM:** REGISTRO/ALMACENAMIENTO OBLIGATORIO — sección Wearable/Sensado → Hardware/MCU.

## P-SEN-012 — ESP32-S3

- **ID:** P-SEN-012
- **Autor/organización:** Espressif Systems
- **Título:** ESP32-S3 Datasheet
- **Versión consultada:** v2.2
- **Tipo:** Datasheet oficial del SoC
- **URL:** https://www.espressif.com/en/support/download/documents
- **Área principal:** Wearable / Sensado
- **Áreas secundarias:** MCU; SPI; USB; Wi-Fi; BLE
- **Estado:** ACEPTADA
- **Motivo de inclusión:** fuente primaria para capacidades del SoC ESP32-S3 utilizadas al justificar el MCU seleccionado.
- **Aplicación:** D-007; periféricos; comunicaciones; firmware.
- **NotebookLM:** REGISTRO/ALMACENAMIENTO OBLIGATORIO — sección Wearable/Sensado → Hardware/MCU.

## Fuente candidata no aceptada todavía

**STEVAL-MKI245KA — STMicroelectronics**

Permanece como **FUENTE/COMPONENTE CANDIDATO** para carrier de prototipo del ISM330BX. No recibe ID definitivo hasta decidir si se adopta como hardware del proyecto.
