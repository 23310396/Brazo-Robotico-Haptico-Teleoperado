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

## P-SEN-013 — STEVAL-MKI245KA

- **ID:** P-SEN-013
- **Autor/organización:** STMicroelectronics
- **Título:** STEVAL-MKI245KA — ISM330BX evaluation kit / official product and data brief
- **Tipo:** Documentación oficial de kit de evaluación
- **URL:** https://www.st.com/en/evaluation-tools/steval-mki245ka.html
- **Área principal:** Wearable / Sensado
- **Áreas secundarias:** IMU; carrier; prototipado; adquisición; montaje
- **Estado:** ACEPTADA — 22 de septiembre de 2026
- **Motivo de inclusión:** carrier oficial adoptado para la primera validación física D-006; expone el pinout del ISM330BX, incorpora desacoplos y facilita montaje temporal reproducible.
- **Aplicación:** D-007; prototipo físico D-006; integración de 3 × ISM330BX.
- **Limitación:** no se adopta como carrier definitivo de la manga; su costo/tamaño pueden justificar una carrier compacta posterior.
- **NotebookLM:** REGISTRO/ALMACENAMIENTO OBLIGATORIO — sección Wearable/Sensado → Hardware/IMU / Carrier.
