# D-005 — Integración modular del manipulador 6R con plataforma humanoide

**Estado:** DECISIÓN ADOPTADA  
**Fecha:** 31 de agosto de 2026  
**Área principal:** Arquitectura mecánica / Robot  
**Impacta:** workspace, montaje, cinemática, colisiones, estructura, validación y modularidad

## Contexto

El asesor técnico está desarrollando una plataforma humanoide que actualmente dispone de torso, cuello y cara, y propuso integrar el manipulador de este proyecto como uno de sus miembros superiores.

El núcleo de la tesis se mantiene sin cambio: desarrollar y evaluar una interfaz wearable con retroalimentación háptica para la teleoperación de un manipulador robótico.

La plataforma humanoide se adopta como **plataforma física de integración**, no como nuevo objeto de investigación de la tesis.

## Decisión

Integrar el manipulador del proyecto como un **módulo serial 6R de 6 grados de libertad**, compatible con la región del hombro del torso humanoide y desmontable para operación independiente sobre una base o fixture de mesa.

No se diseñará un hombro anatómico o esférico complejo. La base del manipulador 6R se fijará estructuralmente en la región correspondiente al hombro del torso.

Durante la teleoperación evaluada por esta tesis, el torso humanoide se considerará fijo; por tanto, la transformación torso → base del manipulador se tratará como constante durante operación.

## Configuraciones requeridas

El mismo manipulador deberá poder utilizarse al menos en dos configuraciones:

1. **Configuración humanoide:** montado en la región del hombro del torso.
2. **Configuración independiente:** montado en una base/fixture de mesa para desarrollo, demostración, pruebas y validación.

La tesis no dependerá de que el resto del humanoide esté terminado para poder validar el manipulador y la interfaz de teleoperación.

## Objetivo de workspace

La geometría 6R deberá diseñarse para cubrir una región frontal de manipulación, incluyendo superficies tipo mesa, permitiendo desplazamientos laterales, verticales y frontales del efector final y control de orientación cuando la tarea lo requiera.

El workspace final dependerá de:

- disposición de los seis ejes;
- longitudes de eslabones;
- límites articulares;
- método de cinemática inversa;
- geometría del montaje;
- restricciones de colisión con torso y cabeza.

## Alternativas consideradas

### A. Mantener el manipulador únicamente como brazo independiente de mesa

**Ventaja:** menor dependencia mecánica de otra plataforma.  
**Desventaja:** desaprovecha la oportunidad de integración real con la plataforma humanoide del asesor.

### B. Diseñar un hombro antropomórfico/esférico complejo

**Ventaja:** mayor similitud anatómica con un brazo humano.  
**Desventaja:** incrementa considerablemente complejidad mecánica, control, fabricación y riesgo de alcance sin ser necesario para la pregunta principal de investigación.

### C. Manipulador serial 6R modular hombro/mesa — SELECCIONADA

**Ventaja:** conserva la arquitectura 6 GDL ya adoptada, permite integración con el humanoide, desacopla la teleoperación de la anatomía exacta del operador y mantiene una ruta de validación independiente mediante base de mesa.

## Justificación

La integración es compatible con las decisiones técnicas existentes y no requiere modificar el núcleo del sistema de teleoperación.

La movilidad tridimensional no depende de reproducir una articulación humana de hombro, sino de la geometría total de la cadena serial 6R, sus límites y la solución de IK.

La modularidad reduce el riesgo de dependencia del humanoide y permite continuar desarrollo y validación aun cuando el torso no esté disponible.

## Impacto sobre decisiones previas

Esta decisión **no modifica**:

- **D-001:** mapeo cartesiano relativo de pose de mano → pose deseada del efector → IK continúa como candidata principal.
- **D-002:** captura del operador mediante 3 IMUs en brazo, antebrazo y mano.
- **D-003:** sensado directo de fuerza mediante strain gauge / load cell en el gripper.
- **D-004:** retroalimentación vibrotáctil para el MVP.
- Arquitectura del manipulador: 6 GDL.

## Gripper y herramientas

El efector principal del MVP será un **gripper de pinza**.

Su diseño y selección permanecen pendientes.

Se conserva como **PROPUESTA OPCIONAL** una interfaz mecánica intercambiable para futuros efectores, por ejemplo una ventosa. Esta interfaz no forma parte del MVP actual.

Un posible canal auxiliar del wearable para activar funciones específicas de futuras herramientas tampoco constituye una decisión actual.

## Payload

**PENDIENTE DE DEFINICIÓN.**

Existe como referencia preliminar de conversación la manipulación de objetos de aproximadamente **1 kg**, pero este valor **no constituye un requerimiento**.

El payload definitivo deberá establecerse después de cerrar la tarea experimental y dimensionar estructura, actuadores, transmisión, gripper y factores de seguridad.

## Datos pendientes del asesor

Para el diseño detallado deberán solicitarse, cuando estén disponibles:

- CAD del torso;
- posición y dimensiones disponibles en hombro;
- material y estructura del torso;
- patrón/forma de montaje;
- altura del hombro;
- masa y soporte del torso;
- restricciones de masa del brazo;
- alimentación disponible;
- infraestructura de control y comunicación;
- restricciones estéticas o dimensionales.

Estos datos son entradas pendientes de diseño y **no condicionan la decisión arquitectónica de integrar el brazo**.

## Riesgos introducidos

- carga estructural en unión hombro–torso;
- momento debido al peso propio del brazo y payload;
- flexión y vibración;
- colisiones brazo–torso/cabeza;
- reducción de workspace por la integración física;
- dependencia dimensional del torso;
- incremento de complejidad mecánica.

## Validación requerida

Antes de cerrar el diseño mecánico deberán verificarse al menos:

- workspace cuantitativo;
- desplazamientos laterales, verticales y frontales requeridos;
- orientación alcanzable;
- límites articulares;
- singularidades relevantes;
- colisiones con torso/cabeza;
- cargas estáticas y dinámicas en la interfaz hombro–torso;
- rigidez estructural;
- masa total y distribución de masas;
- dimensionamiento de actuadores y transmisiones;
- funcionamiento equivalente en montaje de hombro y de mesa.

## Alcance explícitamente excluido

Esta decisión no incorpora a la tesis:

- control del cuello;
- control de la cara;
- locomoción;
- whole-body control;
- coordinación de dos brazos;
- autonomía del humanoide;
- desarrollo integral del torso.

## Trazabilidad

- Contexto Maestro v7 — Integración modular del manipulador con plataforma humanoide.
- Análisis técnico previo realizado en `03 — Robot, cinemática y control`.
- Decisión de integración adoptada en `00 — Dirección del proyecto`.

## Próximos pasos

1. Obtener datos geométricos y estructurales del torso cuando estén disponibles.
2. Cerrar tarea experimental y requerimientos de workspace/payload.
3. Definir geometría candidata de la cadena 6R.
4. Evaluar workspace, singularidades y colisiones en simulación.
5. Dimensionar cargas, actuadores y transmisiones.
6. Diseñar interfaz mecánica modular hombro/mesa.
