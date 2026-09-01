# D-001 — Motion mapping humano → robot

**Estado:** PROPUESTA PRINCIPAL — NO ADOPTADA FORMALMENTE  
**Área principal:** Motion Mapping / Robot  
**Impacta:** variables del wearable, transformación de frames, escalamiento, IK, control y validación

## Contexto

El proyecto requiere transformar el movimiento del miembro superior del operador en comandos para un manipulador serial 6R. La estrategia de mapping condiciona qué variables humanas deben estimarse y cómo se convierten en referencias del robot.

## Propuesta principal

Utilizar **mapeo cartesiano relativo de la pose/movimiento de la mano del operador hacia la pose deseada del efector final**, seguido de cinemática inversa del manipulador.

Flujo conceptual:

`pose/movimiento relativo de la mano → transformación y escalamiento → pose deseada del efector → IK → q1…q6`

El gripper se mantiene como un canal de control independiente.

## Alternativas consideradas

### A. Mapeo articular humano → robot

Relacionar directamente ángulos humanos con articulaciones del manipulador.

**Ventaja:** relación directa entre variables articulares.  
**Limitación:** exige mayor correspondencia entre la anatomía humana y la cinemática del robot y puede complicarse cuando ambas cadenas tienen geometrías diferentes.

### B. Mapeo cartesiano relativo + IK — CANDIDATA PRINCIPAL

Usar la pose/movimiento de la mano como referencia de tarea y resolver las articulaciones del robot mediante IK.

**Ventaja:** desacopla la anatomía exacta del operador de la arquitectura 6R y es compatible con la integración del brazo en humanoide o base de mesa.

### C. Control por velocidad

Convertir el movimiento/intención humana en velocidad deseada del efector o articulaciones.

**Ventaja:** puede ser útil para teleoperación incremental.  
**Limitación:** cambia la relación entre gesto y pose final y requiere evaluación específica de intuitividad y precisión.

## Justificación preliminar

El Estado del Arte v1 identificó al mapping cartesiano relativo como la candidata principal por su compatibilidad con manipuladores cuya geometría no replica la anatomía humana y por permitir controlar la tarea en el espacio cartesiano.

No todas las tareas requieren controlar simultáneamente posición y orientación completas. La dimensionalidad utilizada podrá limitarse cuando la tarea experimental no requiera orientación completa.

## Relación con otras decisiones

- **D-002:** las 3 IMUs deberán proporcionar la información suficiente para estimar el movimiento/pose requerido por este mapping.
- **D-005:** la misma estrategia debe funcionar con el manipulador montado en hombro o en base de mesa mediante la transformación de referencia correspondiente.
- El gripper permanece separado del canal cartesiano principal.

## Pendiente de validación antes de adoptar

- Definir exactamente qué componentes de posición/orientación se controlarán.
- Definir frames humano, wearable, torso/base y efector.
- Definir transformación de calibración entre operador y robot.
- Definir escalamiento espacial.
- Definir clutch/recenter y manejo de saturaciones.
- Seleccionar y validar la IK.
- Evaluar singularidades y límites articulares.
- Evaluar error, precisión, repetibilidad, jitter y latencia.
- Comparar experimentalmente contra las alternativas cuando sea necesario para justificar la adopción.

## Trazabilidad

- Contexto Maestro v7 — sección Motion Mapping.
- Estado del Arte v1 — bloques de motion mapping y sistemas wearable comparables.
- La matriz bibliográfica detallada deberá vincular los IDs de fuentes aceptadas que respaldan, contrastan o sirven como contraejemplo de esta propuesta.

**Nota:** no se asignan aquí IDs bibliográficos no verificados. La trazabilidad fuente → D-001 se completará desde el registro maestro de fuentes aceptadas.

## Próximo criterio de cierre

D-001 podrá pasar a **DECISIÓN ADOPTADA** cuando se cierre la definición funcional del mapping y exista evidencia suficiente de viabilidad para la arquitectura 6R y la tarea experimental.
