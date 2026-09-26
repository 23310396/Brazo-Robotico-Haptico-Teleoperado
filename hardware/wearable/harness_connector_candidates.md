# Investigación de conectores para arnés D-006

**Estado:** INVESTIGACIÓN EXTERNA — PENDIENTE DE APROBACIÓN.  
**Objetivo:** seleccionar un conector de 7 vías para cada ramal del arnés wearable durante D-006.

## Requisitos del ramal

Cada ramal necesita transportar:

1. 3V3
2. GND
3. SCK
4. MOSI
5. MISO
6. CS_i
7. INT1_i

El conector debe:
- tener al menos 7 circuitos;
- estar polarizado;
- soportar cable flexible;
- ser suficientemente compacto para wearable;
- poder montarse/serviciarse sin herramientas especiales de producción;
- tolerar conexión/desconexión durante desarrollo;
- evitar depender de Dupont en el wearable móvil.

## Candidatos

### JST GH — 1.25 mm

Fuente oficial: JST GH connector.

- 7 circuitos disponibles;
- secure lock;
- AWG 30/28/26;
- 1 A con AWG26;
- 50 V;
- housing de 7 vías GHR-07V-S;
- headers de 7 vías disponibles;
- muy compacto.

**Ventaja:** retención mecánica superior para un sistema que se mueve.  
**Limitación:** los headers son SMT; complica un hub construido sólo con placa perforada.

### JST PH — 2.0 mm

Fuente oficial: JST PH connector.

- 7 circuitos disponibles;
- friction lock;
- AWG 32/30/28/26/24;
- 2 A con AWG24;
- 100 V;
- housing PHR-7;
- header through-hole B7B-PH-K-S disponible;
- 7 vías ocupan aproximadamente 15.9 mm en el header.

**Ventaja:** muy fácil de integrar en placa perforada/PCB de prototipo y admite AWG28.  
**Limitación:** retención por fricción, inferior a GH; necesita buen alivio de tensión.

### JST SH — 1.0 mm

Fuente oficial: JST SH connector.

- 7 circuitos disponibles;
- friction lock;
- AWG 32/30/28;
- 1 A con AWG28;
- muy compacto.

**Ventaja:** tamaño mínimo.  
**Limitación:** más delicado para crimpado/manualidad y no aporta bloqueo seguro para D-006.

## Propuesta para D-006

**PROPUESTA:** utilizar JST PH de 7 vías con cable flexible AWG28 para el arnés corporal D-006.

Razones:
- 7 vías exactas;
- montaje through-hole sencillo;
- compatible con placa perforada y prototipado manual;
- AWG28 aceptado por fabricante;
- tamaño todavía compatible con el módulo del XIAO;
- permite construir hub y breakouts de STEVAL sin necesitar una PCB SMT específica.

Para compensar el friction lock se deberá añadir:
- alivio de tensión;
- sujeción del cable al módulo;
- etiquetas permanentes;
- evitar que el peso del arnés recaiga sobre el conector.

**Alternativa para versión más compacta/final:** JST GH de 7 vías si posteriormente se diseña una PCB propia.

## Pinout propuesto del conector de 7 vías

El mismo orden se utilizaría en los tres ramales:

| Pin | Señal |
|---:|---|
| 1 | 3V3 |
| 2 | GND |
| 3 | SCK |
| 4 | MOSI |
| 5 | MISO |
| 6 | CS_i |
| 7 | INT1_i |

La identidad BRAZO / ANTEBRAZO / MANO la determina el puerto del hub y su par CS/INT, no un pinout distinto por cable.

## Fuentes candidatas externas

1. J.S.T. Mfg. Co., Ltd. — GH connector, documentación oficial.
   - Utilidad: secure lock, dimensiones, calibre y número de circuitos.
   - Limitación: requiere header SMT para implementación típica.

2. J.S.T. Mfg. Co., Ltd. — PH connector, documentación oficial.
   - Utilidad: 7 vías, header through-hole, calibres admitidos.
   - Limitación: friction lock.

3. J.S.T. Mfg. Co., Ltd. — SH connector, documentación oficial.
   - Utilidad: contraste de solución ultracompacta.
   - Limitación: friction lock y mayor delicadeza de integración manual.

Estas fuentes permanecen **CANDIDATAS** y no reciben ID del proyecto hasta que la selección sea aprobada.
