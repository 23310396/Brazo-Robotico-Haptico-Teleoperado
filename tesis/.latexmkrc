# Configuración reproducible de latexmk para la tesis.
$pdf_mode = 4; # LuaLaTeX
$out_dir = 'build';
$aux_dir = 'build';
$lualatex = 'lualatex -interaction=nonstopmode -file-line-error -synctex=1 %O %S';

# latexmk detecta biblatex y ejecuta Biber cuando es necesario.
