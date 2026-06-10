[English](README.md) · [Bahasa Indonesia](README.id.md) · **Español**

# Nodo DIY — el sensor de taller

Un nodo ambiental de bajo costo, construible en un fab lab, que publica en la [plataforma Smart Citizen](https://smartcitizen.me/) mediante MQTT. Construido en torno a un **Seeed XIAO ESP32-S3** y un **BME680** (temperatura, humedad, presión, gas/VOC), opcionalmente ampliado con un **Seeed Grove HM3301** para material particulado en exteriores. Dos variantes:

- **Basic** (XIAO + BME680) — ~USD 15–25. Monitoreo de calidad del aire en interiores, clima, riesgo de moho, VOC y hábitat de mosquitos.
- **Plus** (Basic + HM3301) — ~USD 35–60. Añade PM1 / PM2.5 / PM10 en exteriores para quemas, tráfico y polvo de construcción.

El mismo firmware ejecuta ambas variantes: para Basic, simplemente no conectas el HM3301 y dejas sus IDs de sensor en 0 en la configuración. Tiempo de ensamblaje en un taller: ~2 horas para Basic, ~3 horas para Plus, desde el kit hasta verlo en vivo en el tablero.

Este nodo es el **punto de entrada en taller** a la campaña Making Sense Bali. No es un reemplazo de un [Smart Citizen Kit](https://smartcitizen.me/store) oficial (~USD 150): es un complemento de densidad espacial. Sé honesto sobre esa distinción con los participantes del taller.

## Qué es — y qué no es

El nodo DIY existe para **multiplicar la densidad espacial por dólar de campaña**. El SCK 2.1 oficial a ~USD 150 es la columna vertebral confiable: firmware probado en batalla, detección multiparámetro calibrada, plug-and-play. Pero por el mismo dinero que un SCK, la campaña puede enviar 3–4 nodos DIY Plus o 6–10 DIY Basic, desplegados por los participantes en sus propias habitaciones de kos, escuelas, warungs y recintos de banjar. Esa es la palanca: no es que "el SCK sea demasiado caro" (no lo es, para el equipo de campaña), sino que "no podemos poner un SCK en cada kos de Denpasar, y el nivel DIY puede acercarse". Un Basic de USD 20, construido en un taller de Fab Lab Bali y desplegado en la pared del participante, logra que un residente no técnico produzca datos públicos en el mismo tablero en una tarde. Esa densidad es el punto.

Lo que obtienes:

Lo que obtienes de cualquiera de las variantes:

- **Temperatura, humedad y presión barométrica** con una precisión razonable
- **Resistencia de gas (indicador de VOC)** — capta humo de leña, humo de espiral antimosquitos, emisiones de combustibles de cocina, gases de escape de vehículos, productos de limpieza. Se publica como resistencia de gas en bruto en ohmios; menor = más VOC. El firmware también publica un **índice IAQ abierto** (0–500, menor = más limpio) calculado en el dispositivo: una aproximación relativa, no el índice calibrado Bosch BSEC. Consulta las notas de despliegue.
- **Un registro de dispositivo Smart Citizen** que aparece en el tablero de la campaña junto a los SCK oficiales y las estaciones OpenAQ / Sensor.Community
- **Un artefacto pedagógico** — los participantes salen del taller entendiendo I²C, el firmware de ESP32, MQTT y qué significa que "tus datos son públicos"

Lo que obtienes adicionalmente con **Plus**:

- **Lecturas de PM1 / PM2.5 / PM10** suficientemente buenas para detectar eventos de quema de arroz, picos de tráfico y polvo de construcción
- **Triangulación de eventos de combustión** — solo es posible con gas y PM en el mismo nodo (ver casos de uso más abajo)

Lo que no obtienes:

- El sensor de ruido, eCO₂, luz o PM corregido por presión ambiente del SCK
- Las lecturas calibradas y compensadas por deriva del SCK (la deriva del sensor de PM en la humedad tropical es real, ver las notas de despliegue)
- Una carcasa estanca IP65 (la imprimirás en el taller; el SCK oficial viene listo)
- Cinco años de ingeniería de firmware del equipo de Fab Lab Barcelona

Cuando la campaña reporta datos de nodos DIY, se reportan **como tales**: con un marcador distinto en el tablero y una información emergente que explica la menor fidelidad. Mezclar kits DIY y oficiales en silencio sería deshonesto y erosionaría la credibilidad de la campaña en las conversaciones con el gobierno regional que la campaña alimenta.

## Dos variantes — Basic y Plus

### Basic — XIAO ESP32-S3 + BME680 (~USD 15–25)

| Cant. | Pieza | Dónde | Notas |
|---|---|---|---|
| 1 | Seeed XIAO ESP32-S3 | Tokopedia (busca "XIAO ESP32S3"), Shopee, distribuidor de Seeed en Indonesia | ~Rp 250–350k. La variante Sense también sirve, pero la cámara no se usa; el XIAO estándar es más barato. |
| 1 | Placa de conexión GY-BME680 (6 pines) | Busca "BME680" en Tokopedia, los clones genéricos chinos funcionan | ~Rp 150–300k. **Verifica que la marca del IC diga BME680**, no BME280 ni BMP280: a veces los vendedores los etiquetan mal. El BME680 es el único de esa familia con sensor de gas/VOC. |
| 1 | Cable USB-C + fuente de alimentación 5V/1A | Cualquier lugar | El consumo del kit Basic es modesto; un cargador de teléfono sirve. |
| ~4 | Cables puente de 22 AWG | Cualquier tienda de electrónica en Denpasar | Mantenlos cortos: los puentes largos añaden ruido al I²C. |
| 1 | Protoboard sin soldadura (prototipado) + perfboard de 4×6 cm (despliegue) | Tokopedia "PCB matrix board" | Una de 4×6 cabe el XIAO + BME680 con espacio de sobra y coincide con la carcasa impresa. Un montaje de 5×7 también funciona: regenera los STL de la carcasa con `pb_w=50, pb_h=70`. O salta directo a un PCB impreso en la fresadora de Fab Lab Bali para producciones por lotes. |
| — | Carcasa impresa en 3D (PETG, no PLA) | Fab Lab Bali | El PLA se ablanda con las temperaturas de las azoteas de Bali. El PETG aguanta. Diseño paramétrico + STL + guía de impresión: [`enclosure/`](enclosure/). |

### Plus — Basic + sensor de PM HM3301 (~USD 35–60)

Todo lo de Basic, más:

| Cant. | Pieza | Dónde | Notas |
|---|---|---|---|
| 1 | Sensor láser de PM2.5 Seeed Grove HM3301 v1.0 | Directo de Seeed, o Tokopedia "Grove HM3301" | ~Rp 450–600k. El mayor factor de costo del kit. |
| (mejora) | Fuente de alimentación USB-C 5V/2A | Cualquier lugar | El ventilador + láser del HM3301 tiene picos de ~80 mA. La fuente de 1A que basta para Basic cae de tensión bajo la carga del sensor de PM. |

### Cómo elegir entre ellas

**Basic** basta si el despliegue es en interiores (habitaciones de kos, casas tradicionales, aulas escolares, puestos de mercado), si el caso de uso es monitoreo de moho / hábitat de dengue / estrés térmico / VOC en interiores, o si el presupuesto del taller es ajustado: más Basics = más cobertura espacial.

**Plus** es necesario para el monitoreo de calidad del aire en exteriores (azoteas, oficinas de banjar, estaciones costeras), para las preguntas sobre quema de arroz y contaminación por tráfico que la campaña ha señalado, o para la triangulación gas+PM que caracteriza *qué tipo* de evento de contaminación estás viendo.

Para un presupuesto de taller de 10 nodos de ~USD 250, puedes enviar: 10 Basics, o 4 Plus + 5 Basics, o cualquier combinación. Estrategia: elige primero los sitios de despliegue según los temas de preocupación de la Fase 1, y luego elige la variante por sitio.

**Nota de abastecimiento para Bali:** el HM3301 es el factor de costo. El distribuidor indonesio de Seeed (Halo Robotics) lo tiene, pero el margen es real. Para un taller que pide 5+ kits Plus, comprar directo de Seeed (Shenzhen → Denpasar) por la vía de envíos de Fab Lab Bali suele ser más barato que el menudeo. Presupuesta 3 semanas de envío.

## Para qué sirven los datos — casos de uso en Bali

El valor del kit no son las lecturas, sino las lecturas interpretadas por personas que viven en un lugar y actúan según lo que ven. Esto es lo que muestran los datos para los temas que esta campaña realmente sigue.

### Hábitat del mosquito del dengue (Basic)

El Aedes aegypti, principal vector del dengue en Bali, se reproduce de forma óptima a 25–30 °C y con una humedad relativa >70 %. Ambas condiciones son lo habitual en las tierras bajas de Bali la mayor parte del año, razón por la cual el dengue es endémico y no estacional como lo es en lugares templados.

Lo que te da el kit Basic no es una "alarma de dengue": es un registro hiperlocal de cuántas horas pasó un banjar, escuela o recinto de kos específico en condiciones óptimas de cría de mosquitos. Superpuesto con los datos de casos del Dinas Kesehatan, la pregunta cambia de "cuántos casos de dengue este mes" a "qué microclimas concentran el riesgo, y qué intervenciones (calendarios de fumigación, vaciado de recipientes con agua) realmente rompieron el ciclo". La mayor parte de la vigilancia regional del dengue va 2–4 semanas por detrás del reporte de casos; la señal ambiental es en tiempo real.

### Moho y salud respiratoria (Basic)

El moho crece cuando la HR se mantiene por encima de ~60 % con temperaturas de 20–30 °C: las condiciones interiores habituales en Bali durante la temporada de lluvias de octubre a abril en la mayoría de las viviendas sin aire acondicionado. Las esporas de moho son un desencadenante documentado de asma y rinitis alérgica, en particular en niños.

El kit Basic permite que un residente vea, con sus propios datos, que su dormitorio pasó ayer 14 horas en condiciones favorables al moho. Eso es accionable: abrir ventanas por la tarde cuando baja la humedad, usar un pequeño deshumidificador, presionar al arrendador sobre la ventilación. "Mi médico dijo que tengo asma" es difícil de accionar. "Tu dormitorio ha estado al 78 % de HR durante la última semana" es más fácil.

### Estrés térmico y trabajo al aire libre (Basic)

El estrés térmico no es solo la temperatura: es la temperatura de bulbo húmedo, una función de T y HR juntas. Los trabajadores al aire libre en Bali (mantenimiento de banjar, construcción, agricultura, cocineros de ceremonias) alcanzan rutinariamente combinaciones peligrosas en las tardes de la estación seca. Un bulbo húmedo por encima de 30 °C deteriora significativamente el trabajo físico; por encima de 33 °C es peligroso en cuestión de horas.

El kit Basic puede calcular un índice de calor para cualquier sitio de despliegue. Montado cerca de una obra, un mercado o un punto de reunión de banjar, da a los trabajadores y a sus empleadores una señal compartida: "este sitio está hoy en condiciones de estrés térmico, programa el trabajo pesado más temprano o haz pausas a la sombra".

### Exposición a VOC y combustión en interiores (Basic)

El sensor de gas del BME680 responde a los compuestos orgánicos volátiles: humo de espiral antimosquitos, emisiones de cocinar con queroseno, productos químicos de limpieza, solventes de pintura, humo de cigarrillo, la volatilización de capsaicina al freír sambal. Una investigación documentada (Liu et al., 2003) halló que una sola espiral antimosquitos durante la noche libera una masa de PM2.5 comparable a quemar ~75–100 cigarrillos, junto con formaldehído en cantidad sustancial.

El kit Basic publica la resistencia de gas en bruto en ohmios; menor = más VOC. Un nodo en una cocina o dormitorio revela patrones: "tu resistencia de gas baja cada noche entre las 9 PM y las 5 AM por la espiral antimosquitos". Eso es una conversación sobre alternativas (mosquiteros, vaporizadores eléctricos, ventilación), no una preocupación vaga sobre "el aire interior".

### PM en exteriores — quema de arroz, tráfico, construcción (solo Plus)

Los peores periodos de calidad del aire exterior de Bali están ligados a la quema de rastrojo de arroz, típicamente de julio a octubre, cuando se queman los campos posteriores a la cosecha en Tabanan, Gianyar y Klungkung. Los picos de PM2.5 de 200–400 µg/m³ a sotavento de los campos en llamas no son raros. El sensor de gas del kit Basic los ve como una señal de VOC, pero la concentración de partículas —la parte con impacto cardiopulmonar documentado en la salud— requiere el HM3301.

El kit Plus también capta corredores de tráfico (cruces de Canggu, Seminyak, Kuta en hora pico), polvo de construcción (el auge de villas en Ubud, el desarrollo frente al mar del suroeste) y gases de escape diésel costeros (tráfico de barcos turísticos en Sanur, Padangbai, Amed). Para cualquier despliegue donde la pregunta sea el PM exterior, el Plus es obligatorio.

### Triangulación de eventos de combustión (Plus)

Esta es la capacidad analítica que solo obtienes ejecutando gas y PM en el mismo nodo. Los eventos de calidad del aire dejan firmas distintas:

- **La resistencia de gas baja Y el PM se dispara** = combustión. Quema de basura, humo de leña, gases de escape de vehículos. Ambos se liberan juntos.
- **El PM se dispara, el gas estable** = polvo. Construcción, polvo de carretera levantado por el tráfico, ceniza sin quema activa. Sin VOC.
- **La resistencia de gas baja, el PM estable** = vapor. Solventes, pintura, combustible, productos de limpieza. VOC sin partículas de combustión.

Este análisis de firmas permite que la campaña diga algo más que "el aire está mal": le permite decir *qué tipo* de mal, lo que tiene implicaciones de política distintas. Un hallazgo de "polvo de construcción" impulsa una conversación (riego de la obra, límites de horario de trabajo); un hallazgo de "evento de quema" impulsa otra (calendarios de recolección de residuos, reglas de quema a nivel de banjar); un hallazgo de "vapor" impulsa una tercera (ventilación del lugar de trabajo, almacenamiento de químicos domésticos).

Esta triangulación es una capacidad exclusiva del kit Plus y un resultado de investigación significativo más allá de lo que mide el SCK oficial: el SCK tiene eCO₂ mediante el CCS811 pero no resistencia de gas en bruto.

## Dónde encaja esto — los niveles de sensores de la campaña

El nodo DIY no es un instrumento independiente; es un nivel de una red de detección multifidelidad. Making Sense Bali está construido (o aspira a construirse) en cuatro niveles, cada nivel inferior referenciado contra el de arriba. Esa cadena de referencia es lo que separa "la campaña publicó un tablero" de "la campaña publicó datos que el gobierno regional citó en una decisión de política". Sin ella, cada lectura lleva un asterisco; con ella, la campaña puede publicar intervalos de confianza, derivar conteos de eventos y respaldar agregados estacionales.

| Nivel | Hardware | Costo | Rol | Cantidad típica |
|---|---|---|---|---|
| **0 — Referencia** | BAM-1020, Met One E-BAM, Aeroqual AQM 65, o estación BMKG / Udayana alojada | USD 5.000–25.000+ | Verdad de campo (ground truth). Grado regulatorio o casi regulatorio. Ancla de calibración para todo lo de abajo. | 1 por biorregión, alojada por un socio institucional |
| **1 — Smart Citizen Kit 2.1** | SCK oficial de [smartcitizen.me](https://smartcitizen.me/store) | ~USD 150 | Columna vertebral multiparámetro confiable (PM, eCO₂, ruido, clima, luz). Firmware probado en batalla. | 3–10, desplegados por el equipo de campaña |
| **2 — DIY Plus** | Este repo, con HM3301 | ~USD 35–60 | Densidad espacial en sitios exteriores. Las mismas métricas de PM + clima que el SCK pero con menor fidelidad. | 10–50, desplegados por los participantes tras los talleres |
| **3 — DIY Basic** | Este repo, sin HM3301 | ~USD 15–25 | Alcance máximo. Casos de uso de AQ en interiores, clima, VOC, moho / dengue / calor / combustión en interiores. | Muchos — escuelas, kos, banjars, casas particulares |

### La cadena de calibración

Cada nivel se calibra contra el de arriba. **Las correcciones viven en la capa de procesamiento del tablero (`data.js`, el Cloudflare Worker), no en el firmware**: las correcciones de firmware no son auditables, las del tablero están versionadas y son reproducibles.

**Nivel 0 → Nivel 1.** Un BAM-1020 directamente es una compra de USD 25k más mantenimiento anual, que la campaña no asumirá por su cuenta. La vía pragmática para Bali es una alianza con **BMKG (Stasiun Klimatologi Bali, Sanglah)** para la coubicación en sus estaciones climáticas de referencia existentes, o con la **Facultad de Ingeniería o la Escuela de Salud Pública de la Universidad Udayana** para alojar un instrumento de nivel medio como el Aeroqual AQM 65 (~USD 8–15k, robusto en humedad tropical, menor mantenimiento que un BAM). Ambas rutas son conversaciones, no adquisiciones.

**Nivel 1 → Nivel 2.** Los SCK oficiales se coubican con la referencia de Nivel 0 durante una semana en cada estación (seca, húmeda, transición). El tablero deriva un factor de corrección por SCK y por estación. Tras el sprint de calibración, los SCK se despliegan por la biorregión como la columna vertebral confiable.

**Nivel 2 → Nivel 1.** Los nodos DIY Plus se coubican con un SCK calibrado durante ~5 días en su primer despliegue. Se deriva un factor de corrección para el HM3301 del nodo Plus contra el SCK local. A partir de entonces, los datos del Plus son "corregidos por SCK": utilizables para análisis de tendencias y detección de eventos, marcados en el tablero como derivados, no primarios.

**Nivel 3 → Nivel 1.** Los nodos DIY Basic no llevan PM, así que la calibración de PM no aplica. La temperatura y la humedad reciben una verificación de cordura contra el SCK más cercano; la resistencia de gas es una señal relativa que no necesita calibración absoluta (menor = más VOC es cierto independientemente de la referencia).

### Cómo se ve una red realista

Para una biorregión del tamaño del sur de Bali:

- 0–1 instrumentos de Nivel 0 (según las alianzas)
- 5–8 SCK de Nivel 1 en sitios exteriores estratégicos (oficinas de banjar, Fab Lab socio, nodos de azotea en distintos microclimas)
- 20–40 DIY Plus de Nivel 2 en sitios comunitarios exteriores (escuelas, warungs junto a carreteras, frente al mar)
- 50+ DIY Basic de Nivel 3 en interiores (habitaciones de kos, aulas, casas particulares)

Eso son ~75–100 nodos por aproximadamente el costo de 10–15 SCK por sí solos. Los datos siguen apoyándose en el Nivel 0/1 para la credibilidad, pero es la resolución espacial lo que hace útil al tablero: puedes ver *qué barrio* quema basura los miércoles por la noche, no solo que "el sur de Bali tuvo PM elevado".

### Primeros pasos antes de que la red crezca

Tres acciones concretas, en el orden en que importan:

1. **Abre la conversación con BMKG ahora**, antes de que la campaña necesite los datos de referencia. La Stasiun Klimatologi de BMKG en Sanglah opera instrumentos climáticos de grado de referencia. La petición es pequeña: ¿puede la campaña coubicar uno o dos SCK en el sitio de BMKG durante una semana en cada estación? Esa única cadena de coubicación desbloquea credibilidad para toda la red aguas abajo.
2. **Designa un SCK como la "referencia dentro de la red" de la campaña** incluso antes de que exista el Nivel 0. Elige el que se mantenga con más cuidado y se mueva con menor frecuencia. Sus lecturas se vuelven el puente hasta que exista una referencia adecuada.
3. **Ejecuta el primer taller DIY solo después del paso 2** para que los nodos Plus tengan algo con qué coubicarse. Un DIY Plus desplegado sin ninguna ruta de referencia es un nodo que la campaña no puede defender si se lo cuestionan.

Los factores de calibración en sí —cuándo se tomaron, cuáles son, cómo se aplican en el tablero— pertenecen a `docs/calibration.md` (por escribir; es el siguiente documento accionable después de este README).

## Cableado

El esquema de abajo muestra el cableado **Plus**. Para **Basic**, omite la mitad derecha —las filas del HM3301 en la tabla— y cablea solo el BME680.

Ambos sensores viven en el mismo bus I²C cuando ambos están presentes. Cuatro cables del XIAO van a ambos sensores en paralelo; la alimentación difiere (5V para el ventilador del HM3301, 3.3V para la lógica del BME680).

![Esquema — XIAO ESP32-S3 + BME680 + HM3301 en bus I²C compartido](schematic.svg)

| Pin del XIAO | Etiqueta del XIAO | Va a | Net |
|---|---|---|---|
| 5V | `5V` | HM3301 VCC | Alimentación 5V (ventilador + láser) |
| 3.3V | `3V3` | BME680 VCC | Alimentación 3.3V (lógica) |
| GND | `GND` | HM3301 GND **y** BME680 GND | Tierra común |
| GPIO5 | `D4` | HM3301 SDA **y** BME680 SDA | Datos I²C (compartido) |
| GPIO6 | `D5` | HM3301 SCL **y** BME680 SCL | Reloj I²C (compartido) |

La placa de conexión del BME680 expone los pines SDO y CS. Deja SDO flotante (o conéctalo a GND) para la dirección I²C `0x76`. Deja CS en alto (la mayoría de las placas lo manejan internamente). Ignora por completo los pines SPI.

**Direcciones I²C en este bus:**

- BME680 → `0x76` (o `0x77` si conectas SDO a 3V3 — solo relevante si pones dos BME en el bus)
- HM3301 → `0x40`

Si tienes `i2cdetect` corriendo en un portátil Linux o quieres un sketch, escanea el bus primero para confirmar que ambas direcciones aparecen. Si solo aparece una, revisa la alimentación y luego las resistencias pull-up (el XIAO tiene pull-ups débiles internas, pero el cable Grove del HM3301 asume que existen pull-ups externas en algún punto del bus —normalmente las aporta la placa del BME680).

## Plataforma Smart Citizen — registra el dispositivo

Antes de flashear, configura el dispositivo en Smart Citizen:

1. Inicia sesión en [smartcitizen.me](https://smartcitizen.me/).
2. Añade un nuevo dispositivo. Elige **"Other devices"** → hardware personalizado. Dale un nombre como `Bali DIY Node — [location]`.
3. Añade los sensores que vas a publicar. Para este kit:

   **Ambas variantes:**
   - **Temperature** (°C) — BME680
   - **Humidity** (%) — BME680
   - **Pressure** (hPa) — BME680 *(opcional, deja el ID del firmware en 0 para omitirlo)*
   - **Gas resistance** (Ω, en bruto) — indicador de VOC del BME680
   - **IAQ** (índice, 0–500) — BME680, calculado en el dispositivo (aproximación abierta)

   **Solo la variante Plus — añade también estos:**
   - **PM1** (µg/m³) — HM3301
   - **PM2.5** (µg/m³) — HM3301
   - **PM10** (µg/m³) — HM3301

   Para un kit Basic, simplemente deja los IDs del sensor de PM en 0 en la configuración del firmware; el paso de publicación omite cualquier sensor con ID 0.
4. Fija la ubicación en las coordenadas de despliegue (no la geolocalización por IP de tu portátil — la azotea real).
5. Desde la página del tablero del dispositivo, copia el **token del dispositivo** (usado para la autenticación MQTT) en el firmware. No necesitas copiar los IDs de los sensores: el firmware ya usa los IDs del catálogo global de Smart Citizen (233–241), y la plataforma los mapea automáticamente a tu dispositivo en la primera publicación.

El token del dispositivo es lo que autentica el nodo ante la plataforma. Puede revocarse desde el tablero si un kit se pierde —trátalo como una contraseña.

## Firmware

Dos sketches en este repo. **Flashea primero el sketch de prueba.**

### Sketch de prueba — herramienta de arranque, sin plataforma

[`firmware/diy_node_test/diy_node_test.ino`](firmware/diy_node_test/diy_node_test.ino) es un sketch solo de verificación. Escanea el bus I²C, sondea ambos sensores e imprime lecturas en el Serial Monitor cada 5 segundos. **No requiere WiFi, ni MQTT, ni cuenta de Smart Citizen.** Esto es lo que un participante del taller flashea justo después de soldar: si aparecen números sensatos en el Serial Monitor, el hardware funciona y puede pasar al firmware completo con confianza. Si no, el escaneo I²C y la salida del sondeo por sensor del sketch de prueba suelen apuntar directo al problema de cableado o de alimentación.

Funciona tanto para los kits Basic (solo BME680) como Plus (BME680 + HM3301): el sketch de prueba detecta qué sensores están presentes e imprime solo lo que encuentra.

### Sketch de producción — publica en Smart Citizen

**El mismo sketch ejecuta Basic y Plus.** Para Basic, la inicialización del HM3301 al arrancar devuelve "NOT FOUND", el firmware lo registra una vez y omite la publicación de PM en cada ciclo. Sin cambios de código —simplemente no conectes el HM3301 y deja sus tres IDs de sensor en 0 en el bloque de configuración.

El sketch de firmware de producción está en [`firmware/diy_node/diy_node.ino`](firmware/diy_node/diy_node.ino). Este:

- Arranca el I²C y sondea ambos sensores al arrancar
- Se conecta al WiFi y sincroniza el reloj vía NTP (la plataforma requiere marcas de tiempo `recorded_at` reales)
- Lee temperatura, humedad, PM1, PM2.5, PM10 cada 60 segundos
- Publica un mensaje MQTT por ciclo en `device/sck/{DEVICE_TOKEN}/readings` en `mqtt.smartcitizen.me:8883` (TLS)
- La forma del payload coincide con el formato documentado de la plataforma (`data` → `recorded_at` + `sensors[]`)

Bibliotecas de Arduino requeridas (instálalas vía Library Manager):

- `Adafruit BME680 Library` (depende de `Adafruit Unified Sensor`) — nota: **no** la biblioteca BME280
- `PubSubClient` de Nick O'Leary (MQTT) — solo la necesita el sketch de producción
- `ArduinoJson` v7.x — solo la necesita el sketch de producción

El HM3301 se lee directamente por I²C —no hace falta una biblioteca externa. Mira la nota de abajo sobre el porqué.

Placa: instala el paquete **esp32 by Espressif Systems** en el board manager del Arduino IDE, luego selecciona **XIAO_ESP32S3**.

**¿Por qué no la biblioteca Seeed_HM330X?** El driver de Arduino para el HM3301 de Seeed está escrito contra la antigua toolchain de Arduino AVR y usa alias de tipo no estándar `u8` / `u16` / `u32` sin definirlos. El core moderno arduino-esp32 no provee esos typedefs, así que el propio archivo `.cpp` de la biblioteca falla al compilar con `error: 'u32' has not been declared`. Un shim de typedef en el sketch no puede arreglar esto —el `.cpp` de la biblioteca es una unidad de traducción separada.

En lugar de parchear una biblioteca de proveedor en la máquina de cada desarrollador, ambos sketches de este repo hablan con el HM3301 **directamente por I²C**. Es un único `Wire.write(0x88)` al arrancar para seleccionar el modo I²C, y luego `Wire.requestFrom(0x40, 29)` por cada trama de datos de 29 bytes. La disposición de la trama (según la hoja de datos del HM-3300/3600) está documentada en línea encima de la función `readHM3301` —los PM1/PM2.5/PM10 atmosféricos están en buf[10..15], más una suma de comprobación en buf[28] que verificamos antes de confiar en la lectura.

Costo total: ~15 líneas de código, cero dependencias externas para este sensor.

Edita el bloque de configuración en la parte superior de `diy_node.ino`. Solo fijas tres valores, todos marcados con marcadores de posición `YOUR_*`: `WIFI_SSID`, `WIFI_PASSWORD` y `SC_DEVICE_TOKEN` (de la página de tu dispositivo). Los IDs de sensor (233–241) son IDs del catálogo global de Smart Citizen y vienen prellenados —déjalos como están; para un kit Basic, fija los tres IDs de PM (233/234/235) en 0 para omitirlos. Flashea, abre el serial monitor a 115200 baudios y observa la secuencia de conexión. En un par de minutos el dispositivo debería aparecer "online" en smartcitizen.me con las lecturas fluyendo.

Si las lecturas no aparecen: comprueba que los IDs de sensor en el firmware coincidan exactamente con los de la página del dispositivo en SC (son numéricos y por dispositivo), y que el dispositivo no se haya marcado como "private" —público es el valor por defecto.

## Ruta de prototipado

No te saltes pasos. Cada uno aísla una clase distinta de error.

**Etapa 1 — Protoboard, alimentado por USB, en tu taller. Primero el sketch de prueba, luego producción.** Cabléalo con puentes. **Flashea primero `diy_node_test.ino`** y confirma lecturas sensatas en el Serial Monitor —esto prueba que el hardware funciona de forma aislada, sin configuración de nube. Solo después, cambia a `diy_node.ino`, completa las credenciales de WiFi y el token del dispositivo / IDs de sensor de Smart Citizen, y confirma que el dispositivo aparece en smartcitizen.me. Dividir el arranque de esta manera aísla los errores de hardware de los de plataforma —si ambos funcionan en secuencia, estás sólido.

**Etapa 2 — Perfboard, alimentado por USB, en interiores.** Suelda sobre una placa de matriz de 4×6 cm (el tamaño que asume la carcasa impresa). Usa **headers hembra** para el XIAO y el BME680 —son las piezas con más probabilidad de morir por un error de cableado o una sobretensión, y conviene poder cambiarlas sin desoldar. Para el montaje Plus, suelda cuatro cables a los puntos de prueba del soporte del HM3301 en lugar de usar el cable Grove —la carcasa monta el módulo con el zócalo hacia abajo (ver `enclosure/`). Hazlo correr 48 horas en interiores junto a una referencia conocida (una app de calidad del aire en el teléfono apuntada a una ventana sirve para una verificación de cordura). Confirma que las lecturas son estables, que el dispositivo no se reinicia y que el MQTT se reconecta tras una caída del WiFi.

**Etapa 3 — Carcasa, desplegado.** Imprime en 3D la carcasa de PETG de [`enclosure/`](enclosure/) —la "piña" (pine cone): una piel escamada biomimética que es al mismo tiempo el desagüe de la lluvia y la ventilación, con el Grove HM3301 de pie en vertical detrás de una rejilla con barrotes, las ubicaciones de los componentes marcadas por contornos de huella impresos en lugar de texto, y un compartimento opcional para LiPo. Sin soportes, junta con cierre de tornillo, cubre ambas variantes; los cuatro diseños anteriores viven en `enclosure/archive/` con una advertencia. La justificación de diseño y la guía de ensamblaje están en esa carpeta; las notas de despliegue de Bali de más abajo siguen aplicando. Móntala a la sombra, nunca bajo sol directo. Aliméntala con una fuente USB estanca o un panel solar de 5V + convertidor reductor (esto último es un proyecto aparte; empieza con alimentación de pared).

**Etapa 4 — PCB impreso (opcional, para producciones por lotes).** Una vez que un diseño haya corrido de forma fiable en la etapa 3 durante unos meses, diseña una placa portadora a medida en KiCad y fresada en la impresora de PCB de Fab Lab Bali. Esta es la etapa de "nos comprometemos a desplegar 20 de estos", no el primer montaje.

## Notas de despliegue en Bali

La razón de existir de la campaña son los datos, no el firmware. Toma esta parte en serio.

**Humedad.** Bali tiene una humedad relativa del 80 %+ la mayor parte del año. Las placas sin recubrir se corroen en 6–12 meses. Tras la etapa 2, **recubre el lado soldado del perfboard con un recubrimiento conformado de silicona** (MG Chemicals 422B o similar —está disponible en Singapur y se envía a Bali). Enmascara las aberturas del sensor y el conector USB-C antes de rociar. El puerto de humedad del BME680 y la entrada de aire del HM3301 deben quedar sin cubrir. Solo el paso del recubrimiento conformado duplica aproximadamente la vida útil del despliegue.

**Deriva del sensor de PM.** Los sensores derivados de Plantower (el HM3301 está en esta familia) derivan al alza con el tiempo en alta humedad —las lecturas trepan un 30–50 % por encima tras 12–18 meses en condiciones de Bali. **El firmware no compensa esto.** Para un kit de taller, es un compromiso aceptable. Para datos que la campaña use en conversaciones de política, **coubica el nodo DIY con un SCK oficial o una referencia conocida durante al menos una semana**, deriva un factor de corrección y aplícalo en la capa de procesamiento del tablero (no en el firmware —las correcciones pertenecen al pipeline de datos). Este es el mismo patrón que usa Sensor.Community para su red de bajo costo.

**Calentamiento del sensor de gas.** El sensor de gas de óxido metálico del BME680 necesita ~24 horas de operación continua antes de que sus lecturas se estabilicen —el calentador necesita tiempo para quemar los contaminantes de superficie del proceso de fabricación. No confíes en el primer día de datos de resistencia de gas. Después de eso, espera una deriva lenta al alza a lo largo de meses a medida que el elemento sensor envejece —la **tendencia** importa más que el valor absoluto. Para Bali, la señal de gas más útil es la correlación: una caída de la resistencia de gas que coincide con un pico de PM2.5 apunta a combustión (quema de basura, humo de leña); una caída sin PM apunta a solventes o vapor de combustible.

**Carcasa.** El sol + las lluvias de Bali destruirán un nodo mal protegido en semanas. La entrada de aire del HM3301 debe mirar hacia abajo o de lado (nunca hacia arriba —lluvia) y debe protegerse de la entrada directa de insectos (una malla fina de acero inoxidable sobre la entrada ayuda, pero revisa la acumulación de obstrucciones mensualmente). El sensor de humedad del BME680 necesita flujo de aire pero no agua —un enfoque con persianas estilo abrigo meteorológico (Stevenson screen) es el patrón correcto. No lo despliegues en un techo de zinc bajo sol directo sin aislamiento térmico; el BME680 leerá 15 °C de más.

**WiFi.** La fiabilidad del WiFi en Bali va desde "bien" hasta "hoy se cayó el cable a Singapur". El firmware debe reconectarse al perder el WiFi y mantener el dispositivo funcionando localmente incluso sin conexión. El firmware actual descarta lecturas cuando está sin conexión —añadir un pequeño búfer de lecturas no enviadas es una mejora conocida (TODO).

**Alimentación.** La mayoría de los despliegues tendrán alimentación de pared mediante una fuente de 5V/2A. Una pérdida de energía es la causa más común de "el nodo se quedó en silencio" —el participante lo desenchufó para cargar su teléfono. El encuadre del taller ayuda: esto es parte de los datos, etiqueta la fuente claramente con `Smart Citizen — do not unplug`.

## Formato de taller (sugerido)

Un taller de media jornada en Fab Lab Bali, 6–10 participantes, dos constructores por kit (uno suelda, uno flashea; se turnan).

- **Hora 1** — encuadre de la campaña (¿por qué medimos? ¿qué interés tiene un banjar en esto?), recorrido por el tablero, mirar juntos las lecturas existentes
- **Hora 2** — ensamblaje del kit (soldar en el perfboard, cablearlo, aún sin firmware)
- **Hora 3** — flasheo del firmware, configuración de WiFi, registro del dispositivo en smartcitizen.me, primera lectura
- **Hora 4** — decisiones sobre la carcasa (¿dónde vivirá esto? ¿hacia dónde mira? ¿quién lo vuelve a enchufar si se cae de la pared?)

Lo que el participante se lleva a casa: un nodo funcionando, una carcasa impresa, una fuente USB etiquetada y una hoja impresa con la URL del dispositivo en smartcitizen.me y el número de WhatsApp de la campaña al que llamar si deja de funcionar.

Lo que la campaña se lleva del taller: un nuevo punto en el tablero, el permiso del participante para publicar y una persona responsable con nombre en la ubicación de despliegue.

## Licencia

Igual que el repo de la campaña matriz: código MIT, documentación CC-BY-SA 4.0. Haz un fork para Making Sense [tu lugar] y cuéntanos qué cambió.
