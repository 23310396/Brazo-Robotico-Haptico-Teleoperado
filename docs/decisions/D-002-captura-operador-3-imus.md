# D-002 — Captura del operador con 3 IMUs

**Estado:** DECISIÓN ADOPTADA  
**Área principal:** Wearable / Sensado  
**Impacta:** hardware del wearable, calibración, estimación de pose, motion mapping, filtrado y validación

## Contexto

El sistema necesita estimar el movimiento del miembro superior del operador con complejidad y costo razonables, evitando instrumentar innecesariamente toda la anatomía o todos los dedos para el MVP.

## Decisión

Utilizar **3 IMUs** ubicadas en:

1. brazo;
2. antebrazo;
3. mano.

Durante la teleoperación, el torso del operador se considerará aproximadamente fijo.

No se exige reconstrucción anatómica completa del miembro superior como objetivo del MVP.

## Propuesta técnica asociada

- Estimar la posición de la mano mediante una reconstrucción free-segment / cinemática directa geométrica a partir de las orientaciones del brazo y antebrazo.
- Obtener la orientación de la mano desde la IMU instalada en la mano.
- Utilizar calibración sensor-segmento como bloque obligatorio.
- Candidata principal de calibración: combinación funcional + estática.
- Evitar depender continuamente del magnetómetro como condición base.
- Baseline propuesto: gyro + acelerómetro con mecanismo de clutch/recenter.
- Mantener corrección magnética condicionada como alternativa a evaluar.

Estas propuestas asociadas no convierten automáticamente en decisión el algoritmo final de sensor fusion o calibración.

## Alternativas consideradas

### A. Menos IMUs

Reduce hardware, pero limita la información disponible para reconstruir la pose/movimiento del miembro superior.

### B. 3 IMUs — SELECCIONADA

Equilibra información de brazo, antebrazo y mano con complejidad razonable para el MVP.

### C. Instrumentación extensa del brazo/mano

Puede aumentar observabilidad y detalle, pero incrementa costo, calibración, cableado, software y riesgo de alcance sin ser necesario para la pregunta principal de la tesis.

## Justificación

La decisión se adoptó después del análisis del Estado del Arte de captura del operador y de la definición de que el objetivo no es replicar anatómicamente cada articulación humana, sino obtener variables útiles y repetibles para teleoperar el efector del manipulador.

La arquitectura es compatible con D-001, donde la información humana se transforma a una referencia cartesiana del efector final.

## Relación con otras decisiones

- **D-001:** debe entregar las variables necesarias para el mapping cartesiano si éste se adopta.
- **D-005:** no cambia por montar el robot en humanoide o mesa; el wearable sigue capturando al operador de la misma forma.

## Pendiente de validación

- Modelo/componente IMU comercial.
- Algoritmo de sensor fusion.
- Convenciones de marcos.
- Calibración sensor-segmento definitiva.
- Longitudes de segmentos empleadas por el modelo.
- Error de posición y orientación.
- Repetibilidad.
- Drift.
- Frecuencia de actualización.
- Latencia.
- Jitter/ruido.
- Robustez ante errores de colocación.
- Funcionamiento y criterio de clutch/recenter.

## Trazabilidad

- Contexto Maestro v7 — D-002 y bloque de captura del operador.
- Estado del Arte v1 — captura de movimiento / sensado del operador.
- **P-SEN-003 — Kurpath et al. (2024), DOI 10.1016/j.sna.2024.115019**, fuente aceptada relacionada con teleoperación mediante 3 IMUs; acceso restringido, por lo que sólo deben utilizarse detalles verificables.
- La matriz bibliográfica deberá mantener además las fuentes de respaldo, contraste y limitaciones asociadas a calibración y estimación de pose.

## Criterio de validación de la decisión

La arquitectura de 3 IMUs se conservará si las pruebas demuestran precisión, repetibilidad, estabilidad y latencia suficientes para los requerimientos derivados de la tarea experimental.
