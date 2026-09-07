# D-006 — Validar el wearable como subsistema antes de integrar el robot

**Estado:** DECISIÓN ADOPTADA  
**Fecha:** 6 de septiembre de 2026  
**Área principal:** Wearable / Sensado / Estrategia de integración  
**Impacta:** secuencia de desarrollo, validación, motion mapping, adquisición, calibración, visualización y criterios de entrada a integración con robot

## Contexto

El proyecto ya dispone de un pipeline Python independiente del hardware para reconstrucción geométrica del miembro superior a partir de tres orientaciones de segmento, asociado a D-002.

Antes de conectar esta salida al mapping humano → robot y a la cinemática del manipulador, se decidió cerrar primero el wearable como un subsistema físicamente funcional y cuantitativamente validado.

Esta decisión busca evitar propagar errores de sensado, calibración, sincronización o reconstrucción hacia el control del robot, donde sería más difícil distinguir si un comportamiento incorrecto proviene del wearable o del mapping/IK.

## Decisión

Antes de iniciar la integración con el manipulador, se deberá construir y validar una **manga/sistema físico con 3 IMUs** capaz de:

1. adquirir las orientaciones de brazo, antebrazo y mano en tiempo real;
2. mantener referencia temporal/sincronización suficiente entre sensores;
3. ejecutar calibración sensor-segmento;
4. reconstruir geométricamente el miembro superior;
5. entregar posición de codo y muñeca y orientación de mano;
6. mostrar una visualización en tiempo real del miembro superior reconstruido;
7. cuantificar el desempeño del wearable antes de alimentar cualquier mapping hacia el robot.

## Hito funcional previo al mapping humano → robot

La visualización deberá representar como mínimo:

- hombro como referencia;
- brazo;
- codo;
- antebrazo;
- muñeca;
- orientación de la mano;
- orientaciones relevantes de los segmentos.

El objetivo no es únicamente que la animación "se vea correcta", sino utilizarla junto con pruebas cuantitativas para demostrar que el modelo digital sigue al operador de forma suficientemente estable y repetible.

## Criterios que deberán validarse

Antes de pasar a integración con el robot deberán cuantificarse, como mínimo:

- error de reconstrucción/pose;
- estabilidad;
- ruido y jitter;
- drift;
- sincronización entre sensores;
- repetibilidad;
- comportamiento ante errores de colocación/calibración cuando aplique;
- frecuencia efectiva y latencia del pipeline físico cuando estén disponibles.

Los límites numéricos de aceptación permanecen **PENDIENTES DE DEFINICIÓN/VALIDACIÓN** y deberán justificarse con la tarea experimental, literatura aceptada y/o medición.

## Estado de implementación al adoptar la decisión

### IMPLEMENTADO EN SOFTWARE

El pipeline Python ubicado en:

`wearable/sensors/pose_pipeline/`

ya incluye pruebas y análisis para:

- reconstrucción geométrica;
- sensibilidad a error angular;
- error residual de calibración;
- ruido/jitter;
- detección de desincronización en pruebas del pipeline;
- datos sintéticos y pruebas automáticas.

### EVIDENCIA DE CI

GitHub Actions, workflow **Probar wearable**, sobre el commit:

`24d0f955c4a7f4d6f2be37a569c9b768888cdc42` — `Actualización del pipeline con ruido y jitter`

registró:

- 31 pruebas ejecutadas;
- 31 pruebas exitosas;
- resultado final `OK`;
- workflow concluido en `success`.

Esta evidencia valida el estado actual del **pipeline software y sus pruebas automáticas**, no el wearable físico completo.

## Estado todavía pendiente

Esta decisión NO significa que el wearable ya esté validado físicamente.

Permanece pendiente:

- selección de IMU comercial;
- selección de microcontrolador/hardware de adquisición;
- diseño mecánico de la manga/soportes;
- adquisición real de tres sensores;
- timestamp/sincronización real;
- procedimiento físico definitivo de calibración sensor-segmento;
- visualización en tiempo real conectada a sensores reales;
- mediciones de drift y ruido con hardware;
- validación de repetibilidad;
- criterios numéricos de aceptación;
- prueba integrada de extremo a extremo del wearable físico.

## Arquitectura física candidata

Permanece como **PROPUESTA**, no como decisión final de componentes:

```text
3 IMUs
  ↓
microcontrolador
  ↓
PC
  ↓
calibración + reconstrucción + visualización
```

La función candidata del microcontrolador es adquirir, marcar temporalmente y transmitir los datos, manteniendo inicialmente el procesamiento principal en PC para facilitar depuración y validación.

No se adopta todavía un modelo específico de IMU ni de microcontrolador.

## Relación con decisiones previas

- **D-002:** mantiene la captura mediante 3 IMUs en brazo, antebrazo y mano.
- **D-001:** permanece como propuesta principal de mapping cartesiano relativo, pero su integración se pospone hasta validar este hito del wearable.
- **D-005:** no cambia la arquitectura modular del manipulador ni su integración al humanoide.

## Razón de la secuencia

Validar primero el wearable permite separar dos problemas:

1. estimar correctamente el estado/movimiento del operador;
2. transformar esa estimación en comandos para un manipulador.

Si ambos bloques se desarrollaran simultáneamente, un error observado en el robot podría provenir de calibración, ruido, reconstrucción humana, mapping, IK, saturación o control. Esta decisión reduce esa ambigüedad y facilita una validación trazable por subsistemas.

## Criterio de salida de este hito

Se podrá comenzar formalmente la integración humano → robot cuando exista evidencia de que el wearable físico:

- adquiere las 3 orientaciones de forma estable;
- reconstruye el miembro superior en tiempo real;
- permite visualizar y verificar el movimiento reconstruido;
- tiene métricas documentadas de error, jitter/ruido, drift, sincronización y repetibilidad;
- cumple criterios de aceptación definidos para continuar al mapping.

Hasta entonces, el mapping humano → robot puede desarrollarse únicamente de forma desacoplada/sintética, pero no considerarse integrado al sistema físico.

## Trazabilidad

- Contexto Maestro v8 — D-002 y prioridad software-first.
- `wearable/README.md` — objetivo y criterio de paso a integración.
- `wearable/sensors/pose_pipeline/` — implementación actual.
- GitHub Actions `Probar wearable`, run asociado al commit `24d0f955...`.
- Decisión adoptada tras trabajo en `02 — Wearable y sensado`.

## Próximos pasos

1. Continuar el pipeline V1 con las validaciones software faltantes que aporten al hardware real.
2. Definir arquitectura física mínima de adquisición sin seleccionar componentes por intuición.
3. Seleccionar IMUs y MCU con datasheets y requisitos justificados.
4. Construir la manga/soportes físicos.
5. Implementar adquisición, timestamps y sincronización real.
6. Implementar calibración física sensor-segmento.
7. Implementar visualización en tiempo real.
8. Ejecutar protocolo cuantitativo de validación del wearable.
9. Sólo después conectar la salida validada al mapping humano → robot.
