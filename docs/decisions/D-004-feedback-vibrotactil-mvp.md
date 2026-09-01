# D-004 — Retroalimentación vibrotáctil para el MVP

**Estado:** DECISIÓN ADOPTADA  
**Área principal:** Háptica  
**Impacta:** wearable, mapeo fuerza→feedback, latencia, percepción y evaluación experimental

## Contexto

El proyecto requiere comunicar al operador información sobre la fuerza de agarre sin introducir una arquitectura háptica que comprometa alcance, costo, peso o terminabilidad del MVP.

## Decisión

Utilizar **retroalimentación vibrotáctil** como modalidad háptica principal del MVP.

La variable principal a comunicar será la **magnitud de la fuerza de agarre** medida por el subsistema definido en D-003.

La codificación base será mediante **amplitud de vibración**, con un baseline de mapeo proporcional/lineal que incorpore umbral de contacto, zona útil y saturación.

## Alternativas consideradas

### A. Vibrotáctil — SELECCIONADA

Favorece una implementación wearable relativamente simple, ligera y compatible con el objetivo experimental de representar magnitud de fuerza.

### B. Force feedback kinestésico

Se conserva como contraste importante porque puede ofrecer mayor fidelidad y desempeño en determinadas tareas, pero incrementa considerablemente la complejidad mecánica y wearable.

### C. Skin stretch

Alternativa técnicamente válida no seleccionada para el MVP.

### D. Electrotáctil

Alternativa técnicamente válida no seleccionada para el MVP.

### E. Neumática

Alternativa técnicamente válida no seleccionada para el MVP.

## Justificación

El Estado del Arte v1 aportó evidencia de utilidad funcional del feedback vibrotáctil para representar información de fuerza/contacto y para tareas donde la información visual puede ser limitada.

La decisión no implica afirmar que vibrotáctil sea universalmente superior a otras modalidades. Se selecciona por su relación entre utilidad experimental y complejidad para este proyecto.

## Relación con otras decisiones

- **D-003:** recibe como entrada la fuerza cuantitativa del gripper.
- **D-002:** el actuador háptico forma parte del wearable, pero no modifica la arquitectura de captura mediante 3 IMUs.
- **D-005:** la integración del brazo al humanoide no cambia el canal háptico del operador.

## Pendiente de validación

- Actuador comercial.
- Ubicación del actuador en el wearable.
- Frecuencia portadora.
- Umbral de contacto.
- Ganancia fuerza → amplitud.
- Zona muerta.
- Saturación.
- Número de niveles perceptibles si se usa cuantización.
- Comodidad.
- Seguridad perceptual.
- Repetibilidad del estímulo.
- Latencia del canal háptico.
- Evaluación con y sin feedback.

## Trazabilidad

- Contexto Maestro v7 — D-004 y bloque de retroalimentación háptica.
- Estado del Arte v1 — sensado de fuerza y retroalimentación háptica.
- La matriz maestra de fuentes aceptadas contiene los trabajos de respaldo y contraste para vibrotáctil, force feedback y otras modalidades.

**Nota:** los IDs bibliográficos específicos no se rellenan aquí si no están verificados en el registro disponible. Deben añadirse desde el registro maestro de fuentes aceptadas para mantener trazabilidad sin inventar referencias.

## Criterio de validación de la decisión

El canal háptico deberá demostrar estímulo reproducible, latencia compatible con el sistema y utilidad experimental medible antes de utilizarse para sostener conclusiones sobre desempeño del operador.
