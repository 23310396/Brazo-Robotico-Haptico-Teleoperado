# Engineering Decisions

Esta carpeta contiene las decisiones y propuestas técnicas numeradas del proyecto **Brazo Robótico Háptico Teleoperado**.

Cada `D-XXX` conserva su propio archivo para mantener historial, alternativas, justificación, impacto, trazabilidad y validación requerida.

## Índice

| ID | Tema | Estado |
|---|---|---|
| [D-001](./D-001-motion-mapping-cartesiano-relativo.md) | Motion mapping humano → robot | PROPUESTA PRINCIPAL — no adoptada formalmente |
| [D-002](./D-002-captura-operador-3-imus.md) | Captura del operador con 3 IMUs | DECISIÓN ADOPTADA |
| [D-003](./D-003-sensado-directo-fuerza-gripper.md) | Sensado directo de fuerza en gripper | DECISIÓN ADOPTADA |
| [D-004](./D-004-feedback-vibrotactil-mvp.md) | Retroalimentación vibrotáctil para MVP | DECISIÓN ADOPTADA |
| [D-005](./D-005-integracion-modular-humanoide.md) | Integración modular 6R con plataforma humanoide | DECISIÓN ADOPTADA |

## Regla de uso

- No convertir una propuesta en decisión sin justificación y adopción explícita.
- No eliminar silenciosamente decisiones anteriores; si una decisión cambia, documentar qué la reemplaza y por qué.
- Mantener trazabilidad hacia fuentes aceptadas, requerimientos, implementación y validación.
- Los IDs bibliográficos `P-XXX-XXX` son distintos de los IDs de decisión `D-XXX`.
- Cuando exista evidencia experimental, enlazarla o referenciarla desde la decisión correspondiente.
