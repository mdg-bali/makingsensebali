[English](README.md) · [Bahasa Indonesia](README.id.md) · **Español**

# Carcasa del DIY Node v5 — la piña

Un único modelo paramétrico de OpenSCAD ([`enclosure.scad`](enclosure.scad)) genera ambas variantes — **Basic** (XIAO ESP32-S3 + BME680 sobre una perfboard de 4×6 cm) y **Plus** (añade el módulo PM Grove HM3301, vertical). Los STL están en [`stl/`](stl/), las vistas previas en [`img/`](img/), los cuatro diseños anteriores en [`archive/`](archive/) con una advertencia para revisar antes de imprimir.

Una piña ya es una carcasa de exterior: escamas superpuestas que desvían la lluvia hacia afuera y se abren para dejar pasar el aire. La v5 toma prestada toda la idea con exactamente **diez hojas grandes** — cuatro bajas sobre las ranuras de entrada, un par flanqueando la rejilla (tres en el arco medio en la Basic), cuatro altas que se funden en la tapa sobre la salida. La protección contra la lluvia y la ventilación son la misma geometría: cada ranura de respiración se esconde en la sombra de lluvia de una hoja. Cada hoja se imprime sin soportes — invertidas, se convierten en aletas ascendentes de ~40°. Un jitter sembrado (seeded) sobre tamaño, ángulo y azimut mantiene la forma orgánica sin sacrificar la reproducibilidad: mismo `scale_seed`, mismo árbol; las tablas `leaves_plus` / `leaves_basic` del código fuente son la disposición si quieres dirigir tu propio arte.

| | Basic | Plus |
|---|---|---|
| Ø del cuerpo (pared del núcleo) | 66 mm | 66 mm |
| Envolvente de escamas | ~Ø90 | ~Ø90 |
| Altura | 99 mm | 119 mm |
| Piezas impresas | núcleo + capucha | núcleo + capucha |

![Ensamblaje Plus](img/v5_plus_front.png)

## La piel es la función

**Lluvia:** cada escama sombrea la banda de pared que tiene debajo a más de 45°; la tapa cubre las filas superiores; un alféizar a 45° desvía el labio inferior de la rejilla. No hay ninguna línea de visión horizontal hacia ninguna abertura. **Aire:** pequeñas ranuras se esconden en la sombra de lluvia bajo las filas de escamas — entrada baja a la altura del BME680, salida alta bajo la tapa — de modo que la chimenea funciona sin ninguna rejilla visible. **La rejilla PM** se sitúa en un parche sin escamas: barras verticales tipo gecko, tres anillos de sombra en línea con las escamas, y la cara de la lata metálica del módulo a 3–4 mm por detrás con un parche de malla fina pegado sobre sus puertos. La hoja de datos del HM3301 permite puertos laterales; el burn-in y la coubicación con el SCK (README principal) siguen siendo la calibración de verdad.

## Sin etiquetas — huellas (footprints)

Los componentes se ubican por su forma, no por texto, y las formas son reales. En el espinazo: la **huella del XIAO ESP32-S3** — contorno real de 21 × 17,8, sus dos filas de header de 7 pines con paso de 2,54 mm (se alinean con la cuadrícula de la perfboard cuando se miran a través de los agujeros), y el óvalo USB-C en el lado del cable; la **huella del BME680** — contorno, fila de header de 6 pines, cuadrado de la tapa del sensor; un **pictograma de batería** a la altura de la celda. En el suelo: un **pictograma USB** en el arco del cable, el **labio/marco de la LiPo** que ubica físicamente la celda, y dos **clavijas de registro** en las posiciones de los agujeros Ø3,2 del carrier Grove verificadas en Eagle — cuando el módulo llega al fondo de sus rieles, las clavijas encajan con un clic, y eso *es* la comprobación de que está asentado y orientado.

## LiPo, con los ojos abiertos

Una 803040 opcional (~1000 mAh) cableada a los pads BAT del XIAO antes del ensamblaje. Basic: se apoya en el marco impreso del suelo, sujeta con bridas. Plus: pegada con cinta de espuma a la parte trasera del carrier dentro de su contorno impreso; el labio del suelo evita que se deslice. Una celda de bolsa (pouch cell) envejece rápido con el calor de Bali — solo celdas protegidas de calidad, revísala al limpiar la malla, el USB sigue siendo la fuente de alimentación permanente. `with_battery=false` elimina las previsiones.

## Impresión

PETG blanco (o PLA+ con relleno de madera para piñas de demostración de interior — el exterior sigue siendo PETG), capas de 0,2 mm, 4 perímetros, sin soportes, refrigeración de pieza encendida.

| Pieza | Orientación | Notas |
|---|---|---|
| core | tal como se exporta — de pie | brim de 5 mm |
| hood | tal como se exporta — tapa hacia abajo | **brim de 10 mm**; las escamas se imprimen como aletas ascendentes, perímetros exteriores lentos ayudan a las puntas |

La capucha tarda ~4–5 h — diez hojas cuestan mucho menos que el experimento de escamas densas que reemplazaron. Primera impresión: pausa el núcleo a ~20 mm, prueba el ajuste con un recorte de perfboard y el carrier Grove; `fit` / `drop` son los mandos; `can_cx` mueve la rejilla; `scale_seed` vuelve a tirar los dados de la piña.

```sh
openscad -o stl/diy-node-plus-hood.stl -D 'variant="plus"' -D 'part="hood"' enclosure.scad
```

piezas: `core` / `hood` / `plate` / `assembly` · variantes: `basic` / `plus` · flags: `with_battery`, `scale_seed`

## Qué más necesitas

| Cant. | Artículo | Notas |
|---|---|---|
| 1 | parche de malla fina de acero inoxidable ~40 × 40 mm | Plus: pegado a la cara de la lata sobre los puertos |
| 2 | tornillos autorroscantes M3 × 8 | la unión |
| 4 | tornillos de pared + tacos, cabeza plana ≤ Ø8 | bocallaves, separación de ~4 mm |
| 2–3 | bridas | alivio de tensión del USB; marco de la batería de la Basic |
| opc | LiPo 803040 + cinta de espuma | ver arriba |

## Ensamblaje

1. Cuelga el núcleo en 4 tornillos de pared ya colocados — las bocallaves quedan detrás de las placas (el par superior a 30 mm de separación).
2. Suelda los cuatro cables del módulo a los pads de prueba de su carrier; la batería (si la hay) a los pads BAT del XIAO; coloca los componentes contra sus huellas del espinazo antes de soldar la perfboard.
3. La perfboard baja por las ranuras traseras — XIAO en su contorno (arriba), BME680 en su contorno (abajo), USB-C hacia la derecha.
4. Plus: el módulo baja por las ranuras delanteras hasta que las clavijas del suelo encajen en sus agujeros de montaje (eso *es* la comprobación de orientación). El parche de malla ya está en la cara de la lata.
5. El cable USB sale por el arco del suelo — sigue el pictograma — sujeto con brida en el poste, con un bucle de goteo afuera.
6. La capucha baja sobre el espinazo hasta que se asienta en el hombro del vaso; dos tornillos M3 a través del collar.

## Reglas de ubicación

Bajo aleros en una pared a la sombra, a más de 20 cm del suelo, punto ideal de 1,5–2 m, nunca sobre chapa metálica desnuda. Apunta la rejilla en dirección contraria al viento monzónico dominante. Revisa el parche de malla y los drenajes cada mes; cepilla la hojarasca de las escamas mientras estás ahí — la recogen exactamente igual que las piñas de verdad.

## Límites conocidos, con honestidad

No es IP65 — el recubrimiento conformal (README principal) protege la electrónica, las escamas protegen el flujo de aire. La capucha con escamas cuesta más plástico (~55 g frente a los 40 de la v4) y más tiempo de impresión; ese es el precio de la piel, y `archive/v4-column/` sigue siendo la construcción simple y rápida. Las puntas de las escamas son la parte que se te engancha al transportarla — tienen 1,35 mm de grosor y soportan la manipulación, pero no apiles las capuchas en una caja. La actualización al SEN54 tendrá su propia revisión cuando esté validada.

Licencia: MIT, repo principal. Referencia de la placa Seeed: [`ref_hm3301_board.pdf`](ref_hm3301_board.pdf) (CC-BY-SA). Haz un fork para Making Sense [tu lugar] — y vuelve a tirar los dados de `scale_seed` para que tu bosque tenga árboles distintos.
