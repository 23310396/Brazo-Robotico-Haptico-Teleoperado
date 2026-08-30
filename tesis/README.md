# Proyecto maestro LaTeX de la tesis

Este directorio contiene la única versión maestra de la tesis del proyecto **Brazo Háptico Teleoperado**.

## Decisiones vigentes

- Documento modular: `main.tex` ensambla preliminares, capítulos y anexos mediante `\input`; cada capítulo permanece en un archivo independiente.
- Norma académica: APA 7 para redacción, citas, referencias, tablas y figuras.
- Bibliografía: BibLaTeX + `biblatex-apa` + Biber.
- Motor recomendado: LuaLaTeX.
- Automatización de compilación: `latexmk`.
- Los requisitos institucionales de portada/layout que aún no estén confirmados se centralizan en `config/`.

## Estructura

```text
main.tex
referencias.bib
config/
preliminares/
capitulos/
figuras/
tablas/
anexos/
```

## Archivos de configuración

- `config/metadata.tex`: datos de portada y metadatos del PDF. No inventar datos faltantes.
- `config/paquetes.tex`: paquetes generales y layout base.
- `config/apa7.tex`: BibLaTeX APA 7 y formato base de captions APA.
- `.latexmkrc`: compilación reproducible con LuaLaTeX y directorio `build/`.

## Compilación recomendada

Desde `tesis/`:

```bash
latexmk -lualatex -jobname=Tesis_Brazo_Haptico_Teleoperado main.tex
```

Salida esperada:

```text
build/Tesis_Brazo_Haptico_Teleoperado.pdf
```

`latexmk` ejecuta automáticamente las pasadas adicionales de LuaLaTeX y Biber cuando sean necesarias.

Para limpiar auxiliares:

```bash
latexmk -C -jobname=Tesis_Brazo_Haptico_Teleoperado main.tex
```

## TeXstudio

Configurar LuaLaTeX como compilador y Biber como herramienta bibliográfica. Para mayor reproducibilidad, conviene crear un comando de usuario que ejecute el comando `latexmk` anterior desde `tesis/`.

## Bibliografía

`referencias.bib` sólo debe contener fuentes efectivamente citadas en la tesis. Mantener trazabilidad entre:

```text
ID interno del proyecto <-> referencia bibliográfica <-> clave BibLaTeX <-> uso en tesis
```

Los IDs internos (`P-MM-...`, `P-SEN-...`, etc.) no sustituyen las citas visibles APA.

## Estado inicial

La infraestructura se crea sin redactar contenido sustantivo a ciegas. El primer capítulo que debe integrarse con contenido real es `capitulos/02_estado_del_arte.tex`, una vez consolidada la matriz bibliográfica y las claves de `referencias.bib`.

## Compilación automática en GitHub

El repositorio utiliza `.github/workflows/compilar-tesis.yml` para compilar el proyecto automáticamente. GitHub exige que los workflows vivan en `.github/workflows/`; por ello ése es el único archivo de infraestructura de la tesis situado fuera de `tesis/`.

GitHub muestra los archivos `.tex` como código fuente. El PDF renderizado se genera mediante GitHub Actions y queda disponible como artefacto de la ejecución.
