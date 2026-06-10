[English](README.md) · [Bahasa Indonesia](README.id.md) · **Español**

# Archivo de carcasas — versiones reemplazadas

Estos son los diseños que vinieron antes del actual. **Ninguno de ellos debería imprimirse para despliegue tal cual** — cada uno fue reemplazado por una razón concreta, conservado aquí porque el linaje es en sí mismo material de taller: cada carpeta es una lección sobre diseñar para FDM y para piezas reales. Revisa, mejora o canibaliza — no imprimas a ciegas.

| Versión | Qué es | Por qué fue reemplazada |
|---|---|---|
| [`v1-box/`](v1-box/) | Caja tipo abrigo de Stevenson con lamas, 3 piezas planas | Nunca se imprimió. Los paneles planos + las lamas de ranura son pensamiento de cortadora láser — infrautiliza la impresora. Además estaba dimensionada para la lata HM3301 desnuda y una perfboard de 5×7. |
| [`v2-lantern/`](v2-lantern/) | Farol de revolución de sección en D, 2 piezas, encaje a presión | Se imprimió y falló. El alojamiento PM encajaba con la lata desnuda de 40×38, pero el módulo Grove es la lata sobre un **PCB carrier de 80×40**. La unión a presión se atascó: holgura de 0,2 mm, las torres guía colisionaban con la pared del vaso. |
| [`v3-gourd/`](v3-gourd/) | Farol con una base ancha rectangular redondeada para el módulo completo, unión atornillada | Funcionaba sobre el papel, encajaba con el módulo real, la unión quedó resuelta — pero la base de 88×48 lo hace voluminoso. Reemplazado por la columna de módulo vertical. |
| [`v4-column/`](v4-column/) | Columna esbelta Ø66, módulo vertical tras una rejilla con lamas anulares, etiquetas de texto, alojamiento de LiPo | Funcionalmente sólido — su arquitectura central continúa. Reemplazado estéticamente: los anillos lisos y el texto en relieve dieron paso a la piel de escamas de piña y a las guías de huella física. Imprime esta si quieres la construcción más simple y rápida. |

Cada carpeta tiene el `enclosure.scad` paramétrico; regenera los STL con los comandos del [README de carcasas](../README.md) principal. Dimensiones de referencia para el módulo Grove HM3301 (de los archivos Eagle de Seeed, ver [`../ref_hm3301_board.pdf`](../ref_hm3301_board.pdf)): carrier 80 × 40 mm, agujeros Ø3,2 en ±36/±16, lata desnuda de 40 × 38 × 15 encima.

Las lecciones recurrentes, para que el próximo fork no las repita: diseña para el **módulo completo comprado**, no para el sensor desnudo de la hoja de datos; las uniones necesitan topes rígidos, holgura radial de ≥0,5 mm y entradas achaflanadas a tolerancias de FDM; la protección contra la lluvia es geometría (faldones, rupturas de la línea de visión, aberturas hacia abajo), no juntas; y verifica con renders completos — la vista previa de OpenSCAD miente sobre `intersection()` + `rotate_extrude`.
