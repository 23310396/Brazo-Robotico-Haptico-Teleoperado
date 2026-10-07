# Checkpoint — Modelo cinemático 6R y Simulador v2

**Fecha:** 6 de octubre de 2026  
**Estado:** CHECKPOINT DE IMPLEMENTACIÓN / VALIDACIÓN EN SOFTWARE  
**Área:** Robot, cinemática y control

## Propósito

Registrar el estado alcanzado del modelo cinemático paramétrico y del banco de pruebas antes de recibir y comparar las implementaciones/propuestas del profesor.

Este checkpoint **no congela el diseño mecánico del manipulador**.

## Arquitectura cinemática actual

**PROPUESTA EN VALIDACIÓN**

Secuencia conceptual:

```text
Rz - Ry - Ry - Rx - Ry - Rx
```

Interpretación:
- J1: giro lateral desde hombro.
- J2: elevación del brazo.
- J3: flexión de codo.
- J4–J6: muñeca de tres ejes.

Se mantiene como propuesta una muñeca esférica ideal con intersección de J4–J6 para desacoplar posición y orientación en la IK.

## Convenciones

Frame base:
- +x: frente.
- +y: izquierda.
- +z: arriba.

`q = [0,0,0,0,0,0]` representa la referencia matemática del brazo extendido hacia delante.

**No representa HOME ni una posición segura del robot físico.**

## Modelo DH estándar implementado

| i | theta_i | d_i | a_i | alpha_i |
|---|---|---|---|---|
| 1 | q1 | 0 | 0 | +pi/2 |
| 2 | q2 | 0 | L1 | 0 |
| 3 | q3 + pi/2 | 0 | 0 | +pi/2 |
| 4 | q4 | L2 | 0 | -pi/2 |
| 5 | q5 | 0 | 0 | +pi/2 |
| 6 | q6 | 0 | 0 | 0 |

El TCP incorpora una distancia adicional `LT` sobre +z6.

## Implementado y validado en software

- FK completa hasta TCP.
- IK analítica para la arquitectura actual.
- Cálculo del centro de muñeca.
- Ramas `elbow+` / `elbow-`.
- Ramas `wrist+` / `wrist-flip`.
- Detección de target geométricamente inalcanzable.
- Detección de singularidad de muñeca.
- Identificación del caso del centro de muñeca sobre el eje de J1.
- Validación de soluciones mediante FK.
- Simulador web Streamlit + Plotly.
- Presets de prueba y visualización de soluciones.

## Geometría de demo

```text
L1 = 1.0
L2 = 1.0
LT = 0.25
```

Valores sintéticos y adimensionales. No representan dimensiones físicas adoptadas.

## Simulador 6R v2

Ubicación:
- `robot/kinematics/`: matemática FK/IK y pruebas.
- `simulation/arm_6r/`: interfaz, animación y README.

El simulador v2 se considera **cerrado como banco de pruebas cinemático**.

Incluye:
- FK interactiva.
- IK cartesiana.
- múltiples ramas;
- robot fantasma;
- comprobación FK→IK→FK;
- detección de target inalcanzable;
- detección de singularidad de muñeca;
- sliders + entradas exactas;
- presets A/B/C/D;
- estados TARGET / IK / SINGULARIDAD;
- animación en navegador.

## Lo que NO queda validado por este checkpoint

- geometría física final;
- dimensiones reales;
- offsets reales;
- límites articulares reales;
- workspace requerido;
- Jacobiano completo;
- clasificación completa de singularidades;
- autocolisión;
- colisión con torso o entorno;
- planeación de trayectoria;
- dinámica;
- velocidades/aceleraciones reales;
- torques;
- motores;
- transmisiones;
- estructura;
- seguridad física.

## Siguiente comparación

Pendiente recibir el handoff **“Implementaciones del Profesor”**.

La comparación deberá determinar:
1. qué parte del modelo actual puede conservarse;
2. qué ejes, offsets o geometría deben cambiar;
3. si la muñeca esférica continúa siendo viable;
4. si la FK/IK actual puede adaptarse;
5. qué información falta del brazo físico;
6. qué cambios son PROPUESTAS y cuáles ameritan una nueva DECISIÓN.

No seleccionar motores ni congelar dimensiones antes de esta comparación.
