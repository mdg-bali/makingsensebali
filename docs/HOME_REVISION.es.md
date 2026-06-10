[English](HOME_REVISION.md) · [Bahasa Indonesia](HOME_REVISION.id.md) · **Español**

# Making Sense Bali · Informe de revisión de la página de inicio (v2)

**Estado:** informe — sin empezar.
**Responsable de la ejecución:** Claude Code.
**Responsable de la intención:** Tomas Diez (líder de Making Sense Bali).
**Informe complementario:** [`docs/PLATFORM_REVISION.md`](PLATFORM_REVISION.md) — la revisión del panel que acaba de lanzarse. La revisión de la página de inicio se apoya en la capacidad analítica que ese panel ofrece ahora, pero se dirige a un público distinto y a un modo de interacción distinto.
**Última actualización:** 2026-05-30.

---

## 1. Por qué esta revisión

La página de inicio actual (`index.html`, 1234 líneas) se lee como un ensayo editorial: de formato largo, metodológicamente autoconsciente, bien elaborado para alguien dispuesto a desplazarse y a involucrarse. Ese público existe (investigadores, otros capítulos de Fab City, periodistas) y el texto actual les sirve bien. **Pero no es el público principal en el que la campaña necesita crecer.**

El verdadero alcance de la campaña se da a través de tres públicos que no leen los sitios editoriales de principio a fin:

- **Madres en los kos de Denpasar / Canggu / Ubud** que preguntan "¿está mal el aire hoy para mi hijo con asma?"
- **Docentes** que preguntan "¿puedo mostrarle a mi clase datos locales reales sobre algo que respiran cada día?"
- **Funcionarios de gobierno en el Dinas Kesehatan y el DLHK** que preguntan "¿hay aquí evidencia sobre la que pueda actuar?"

Para estos públicos la página actual es demasiado densa, demasiado poco estructurada y —lo más importante— **demasiado escasa en llamadas a la acción**. No necesitan una sección de metodología más larga. Necesitan llegar a la página, ver de inmediato algo relevante para donde viven y tener un siguiente paso evidente.

La revisión aporta:

1. **Un hero que prioriza la gravedad** que responde "¿está mal ahora mismo donde estoy?" en menos de tres segundos, en lenguaje sencillo, con la claridad de un semáforo.
2. **Cuatro llamadas a la acción claras** que funcionan para cada público: reportar, encuesta, involucrarse con los sensores, compartir lo que está pasando.
3. **Tarjetas compartibles** — visuales generados automáticamente sobre lo que ocurre en un barrio / momento concreto, diseñados para difundirse en WhatsApp e Instagram, donde el público ya está.
4. **Secciones específicas por público** — no un selector ("¿eres madre o docente?"), sino secciones limpiamente estructuradas en las que cada público puede encontrar lo que necesita sin desplazarse por lo que no necesita.

La revisión del panel convirtió los datos en una herramienta. Esta revisión convierte la página de inicio en un **mecanismo de distribución** de lo que esa herramienta está encontrando. Sin esto, la campaña produce buenos datos que nadie fuera del bucle de los analistas llega a ver.

## 2. Estado actual — qué existe hoy

| Sección | Líneas | Notas |
|---|---|---|
| Hero ("Bali, made visible") | ~400–410 | Enfocado en la marca. Sin personalización por ubicación. Sin indicador de gravedad. |
| Sección del mapa | ~410–440 | Vive en el inicio; duplica lo que el panel ya hace con más capacidad. Decidir si se mantiene. |
| Feed de reportes | ~440–447 | Oculto por defecto (`display:none`) — proviene del trabajo del panel, aún no aflorado en el inicio. |
| "The state of Bali's air" | ~451–479 | Resumen editorial. Útil para el contexto, actualmente demasiado cargado de prosa. |
| "The reading, translated" | ~479–548 | Ayuda de interpretación — ya hace parte del trabajo que necesitan las madres. Reestructurar para priorizar la gravedad. |
| "Listen. Show. Act." | ~548–589 | Encuadre metodológico. Importante para funcionarios, menos para las madres. Reubicar. |
| "Local lead, credited methodology" | ~589–620 | Linaje / gobernanza. Importante para la credibilidad, especialmente con los funcionarios. |
| "Where we are" | ~620–638 | Cobertura de la red. |
| "Concerns" + Encuesta | ~638–672 | Enlace a la encuesta de la Fase 1. **Una de las cuatro CTA.** Actualmente enterrada en la línea 664. |
| "Eight questions" / Beyond survey | ~674–714 | Detalle de la encuesta + contacto. |
| "Need more detail?" | ~715+ | Enlace al panel. |

Cableado existente que vale la pena preservar:

- **Variables CSS** para la paleta de la marca (azafrán + verde azulado + papel crema) están en la parte superior del archivo y se usan de forma coherente. Consérvalas.
- **`<script src="data.js">`** ya está cargado — la página de inicio ya tiene acceso al estado en vivo de sensores + reportes, solo que no lo aflora visualmente más allá del mapa.
- **La capa de traducción bilingüe** de la revisión del panel debería trasladarse a la página de inicio desde el primer día. No lances un inicio solo en inglés que el panel ya podría servir en bahasa indonesio.
- **El enlace de la encuesta** ya está cableado a través de `#surveyLink` → formulario externo de Airtable.

La página es funcional y coherente con la marca. Esta revisión **no es una reescritura desde cero**: es una reestructuración con unos pocos componentes nuevos y una jerarquía más nítida.

## 3. Estado objetivo — qué construir

### 3.1 Hero que prioriza la gravedad

Reemplaza el bloque hero actual por uno que, al cargar la página, intente detectar el barrio del visitante (API de geolocalización, con un repliegue elegante a un desplegable "elige tu barrio") y muestre:

- **Un número titular** — la peor lectura de PM2.5 de hoy en la localidad del visitante, con una banda de gravedad codificada por color (verde / amarillo / naranja / rojo, según las directrices de exposición diaria de la OMS)
- **Una línea en lenguaje sencillo** en el idioma seleccionado por el visitante — ejemplos:
  - VERDE: *"El aire está limpio hoy en Denpasar. Jugar al aire libre está bien."*
  - AMARILLO: *"El aire está moderado hoy en Canggu. Los grupos sensibles (niños, asma, personas mayores) deberían limitar la actividad prolongada al aire libre."*
  - NARANJA: *"El aire está insalubre hoy en Ubud. Se recomienda mascarilla al aire libre, especialmente para los niños."*
  - ROJO: *"El aire es peligroso hoy en Sanglah. Quédate en interiores, ventanas cerradas, mascarilla afuera."*
- **Una pequeña línea de contexto** — "PM2.5 alcanzó un máximo de 47 µg/m³ a las 14:32 · Directriz diaria de la OMS: 5 µg/m³"
- **Dos botones principales** en el hero: "Report what you see →" (deeplink de WhatsApp) y "What's happening near me →" (desplaza/salta a la sección localizada de abajo)

Si se deniega la geolocalización o no hay ningún sensor cerca del visitante, usa por defecto un agregado de toda Bali ("Air across Bali today: moderate · worst reading: Ubud") y un desplegable destacado "Pick your area".

El hero debe funcionar con enfoque mobile-first (375px de ancho); es donde la mayoría de los visitantes lo verá.

### 3.2 Las cuatro llamadas a la acción

Aflora las cuatro CTA por encima del pliegue O dentro de una sola pantalla de desplazamiento — no enterradas en la línea 664 como está hoy la encuesta. Cada CTA es una tarjeta con un verbo claro y una descripción corta. Redacción sugerida (sujeta a revisión de la voz de marca):

1. **"Report what you're seeing →"**
   *¿Hueles humo? ¿Ves quema de residuos? ¿Notas un olor que ayer no estaba? Envía un mensaje de WhatsApp a nuestro bot, nuestro equipo local lo verifica y se suma al mapa público.*
   Acción: deeplink de WhatsApp al número del bot (ya está en `reports/config.json`).

2. **"Tell us what matters →"**
   *La encuesta de la Fase 1 pregunta a los residentes qué problemas ambientales afectan su vida diaria. Ocho preguntas, 5 minutos, define dónde colocamos los siguientes sensores.*
   Acción: abre el formulario de encuesta de Airtable existente en una pestaña nueva.

3. **"Get involved with sensors →"**
   *Organizamos talleres de construcción de sensores en Fab Lab Bali — arma un nodo de calidad del aire de bajo costo en una tarde, despliégalo en tu tejado o en tu aula. Inscríbete para enterarte del próximo taller.*
   Acción: abre un formulario de inscripción (Airtable o similar — coordínalo con el equipo del componente de reportes). A futuro: esto se convierte en una página de compra de kits; diseña la tarjeta para que pueda cambiar a eso sin reescritura.

4. **"Share what's happening →"**
   *Genera una tarjeta compartible sobre el aire de hoy en tu barrio y publícala donde ya ocurre la conversación — WhatsApp, Instagram, Telegram. Cada compartido ayuda a que más gente vea los datos.*
   Acción: abre la sección de tarjetas compartibles (3.4 más abajo).

Las CTA deben sentirse como opciones de igual peso, no como una CTA hero con tres añadidos. Diseño tipo tarjeta, cuatro en fila en escritorio, dos por dos o apiladas en móvil.

### 3.3 Secciones específicas por público (las tres lecturas)

Debajo del hero + las CTA, tres secciones sustanciales — cada una con un encabezado claro para que el visitante sepa cuál es para él, pero todas visibles (no detrás de pestañas ni de un selector):

**Para familias y residentes** — "Hoy en tu barrio"
- El widget de gravedad del hero, ampliado con el gráfico de las últimas 24 h para PM2.5 (enlace al panel para una vista más profunda)
- Reportes cercanos como un feed corto (3–5 más recientes dentro de ~2km)
- Orientación en lenguaje sencillo: cuándo mantener las ventanas cerradas, cuándo usar mascarillas para los niños, qué significan los niveles de humedad para el asma
- Indicador de riesgo de moho si la humedad del barrio ha estado >60% durante >24 h de forma sostenida
- La CTA "Report what you see" repetida al final de esta sección

**Para docentes y escuelas** — "Lleva los datos a tu aula"
- "Un plan de clase usando datos locales de calidad del aire de Bali" — pitch corto + PDF descargable (escribe un plan de clase v1 mínimo si no existe ninguno; no necesita ser elaborado, solo real)
- Encuadre del taller — "Making Sense Bali para escuelas" — aunque sea aspiracional, nombra lo que se ofrece
- Un ejemplo concreto: "Tus estudiantes comparan el PM2.5 de tu escuela con la directriz de la OMS, y luego con una escuela de Barcelona a través de la red global de Smart Citizen"
- La CTA "Get involved with sensors" repetida al final de esta sección

**Para responsables de políticas y analistas** — "Evidencia sobre la que puedes actuar"
- La política de datos / el linaje de la campaña (gran parte de la sección actual "Local lead, credited methodology" se traslada aquí)
- Descargas agregadas — CSV de los últimos 30 días, resumen mensual en PDF (se puede generar automáticamente cada noche mediante la infraestructura `generate_summary.py` existente en `reports/`)
- "Cómo citar los datos de Making Sense Bali en políticas" — un párrafo corto con el formato de cita sugerido y el correo de contacto
- Enlace al panel para análisis en vivo
- Línea de contacto para la interacción directa con el equipo de la campaña

Cada sección debería tener un ancla visual clara (icono, acento de color) para que el visitante pueda escanear y saltar si no es su público.

### 3.4 Tarjetas compartibles — el mecanismo de crecimiento

Esta es la pieza más novedosa de la revisión y probablemente merezca su propia semana.

**Concepto:** generar tarjetas visuales autodiseñadas que resuman lo que está ocurriendo en una localidad de Bali, en un formato optimizado para compartir en grupos de WhatsApp, historias de Instagram y canales de Telegram — donde los públicos objetivo de la campaña ya pasan su tiempo.

**Plantillas de tarjetas (empieza con estas cuatro):**

1. **"Today in [neighbourhood]"** — PM2.5 actual + banda de gravedad + interpretación en una línea + referencia a la directriz de la OMS + logo de Making Sense Bali + URL
2. **"This week in [neighbourhood]"** — gráfico de tendencia de PM2.5 de 7 días (sparkline) + recuento de picos + categoría de reporte más común + URL
3. **"Mold risk: [neighbourhood]"** — tendencia de RH + días por encima del 60% de RH + nota de riesgo en lenguaje sencillo + URL
4. **"Burning corridor: [neighbourhood]"** — pico de PM combinado + recuento de reportes + recorte de mapa que muestra la zona de origen + URL

Cada tarjeta tiene:
- La firma visual de la campaña (paleta + tipografía de las variables CSS existentes)
- Una marca de tiempo ("as of 14:32 WITA, 2026-05-30")
- El wordmark de Making Sense Bali + la URL corta
- Un código QR (pequeño, en la esquina) que enlaza a la vista relevante del panel

**Opciones de renderizado:**

Opción A (recomendada para v1): renderizado del lado del cliente con canvas HTML. Las tarjetas se construyen como HTML estilizado, se convierten a PNG mediante `html2canvas` o similar, y se descargan con el botón "Download card". Más un botón "Share to WhatsApp" que usa el esquema de URL de compartir de WhatsApp, que abre el WhatsApp del usuario con el texto precargado y un enlace de vuelta al sitio.

Opción B (Fase 2): un Cloudflare Worker que renderice SVG → PNG bajo demanda en una URL como `/share/today/canggu.png`. Esto permite que la metaetiqueta og:image del sitio apunte a una tarjeta recién renderizada, de modo que cuando alguien comparta la URL del sitio en cualquier lugar, la vista previa del enlace sea una tarjeta actual y localizada. De mayor impacto pero con más infraestructura.

**Aceptación requerida:** un visitante en Canggu puede hacer clic en "Share what's happening" en el hero, ver cuatro opciones de tarjeta, elegir "Today in Canggu" y descargarla o compartirla a WhatsApp en dos toques. La tarjeta se ve lo bastante distintiva como para que alguien que la vea en un grupo de WhatsApp la reconozca como Making Sense Bali (y no como una captura genérica de calidad del aire).

### 3.5 Correlaciones aflorando en la página de inicio

El panel ahora muestra la correlación entre los picos de los sensores y los reportes ciudadanos. La página de inicio debería aflorar **una sola correlación reciente, la más llamativa**, como panel narrativo, actualizado a diario. Texto de ejemplo:

> **"Los datos y los residentes contaron la misma historia ayer."**
>
> A las 14:30 en Canggu, el sensor de calidad del aire en Jl. Pantai Berawa registró un fuerte pico de PM2.5 — de 12 a 78 µg/m³ en veinte minutos, muy por encima del umbral insalubre de la OMS. Doce minutos después, un residente a dos calles reportó humo de una obra que quemaba residuos. Las dos señales se confirman entre sí. Fab Lab Bali notificó al Banjar de Berawa para su seguimiento.
>
> [See the data →](/dashboard/) [Read the report →](/dashboard/#report-id) [Report what you're seeing →](whatsapp://...)

Elige la correlación significativa más reciente cada día (el pico más alto con un reporte coincidente, o la localidad más visitada). El panel narrativo hace tangible el valor de la campaña de una forma que los gráficos abstractos nunca lograrán — para el público de funcionarios en especial, este es el artefacto que se cita en las conversaciones.

Para v1, esta narrativa puede ser **curada por humanos** (el operador de Fab Lab Bali elige la historia del día a partir del motor de correlación del panel). La generación automática es la Fase 2.

## 4. Fases sugeridas

**Fase 1 — Hero que prioriza la gravedad + cuatro CTA.** ~4 días.
- Geolocalización + detección de localidad (con repliegue manual)
- Widget de gravedad con interpretación basada en bandas
- Cuatro tarjetas CTA por encima del pliegue
- Diseño mobile-first

**Fase 2 — Reestructuración de las secciones por público.** ~3 días.
- Reorganizar las secciones existentes en los tres bloques específicos por público
- Añadir las piezas que faltan (marcador de posición del plan de clase, orientación de citas, widget de riesgo de moho)
- No perder ningún contenido de metodología existente — reubicarlo

**Fase 3 — Tarjetas compartibles (renderizado del lado del cliente).** ~1 semana.
- Cuatro plantillas de tarjeta como HTML estilizado
- Descarga de PNG con `html2canvas`
- Integración de la URL de compartir de WhatsApp
- Sección "Share what's happening" como la UI anfitriona

**Fase 4 — Narrativa de correlación diaria.** ~3 días.
- Flujo de curación manual primero (archivo JSON editado por el operador, como `data/daily_story.json`)
- Renderizado automático en el inicio a partir del JSON
- Fase 2: selección automática a partir de la salida de correlación del panel

**Fase 5 — Pulido + Bahasa + og:image.** ~4 días.
- Cadenas bilingües (apóyate en la infraestructura `t()` del panel)
- Generación de og:image (Cloudflare Worker, Opción B del §3.4)
- QA móvil, pasada de accesibilidad
- Rendimiento: la página de inicio sigue cargando en <3 s en 3G

Total: ~3,5 semanas. Las fases 1 y 2 aportan la mayor mejora percibida y pueden lanzarse antes de que lleguen las fases 3–5.

## 5. Criterios de aceptación

La revisión está terminada cuando:

- [ ] Un visitante llega a la página de inicio en móvil y en un segundo sabe si el aire está bien en su barrio (asumiendo permiso de geolocalización o un valor por defecto sensato)
- [ ] Las cuatro CTA son visibles por encima del pliegue o dentro de un desplazamiento en un teléfono de 375px de ancho
- [ ] Un docente puede encontrar un plan de clase descargable desde la página de inicio en menos de 30 segundos
- [ ] Un responsable de políticas puede encontrar la orientación de citación de datos y la descarga del CSV en menos de 30 segundos
- [ ] Un visitante puede generar y descargar una tarjeta compartible de su barrio en menos de tres toques
- [ ] Un visitante que comparte la URL del sitio en WhatsApp ve una tarjeta de vista previa de enlace relevante a su localidad (trabajo de og:image de la Fase 5)
- [ ] La narrativa de correlación diaria es visible por encima del pliegue en la página de inicio
- [ ] La página de inicio funciona tanto en inglés como en bahasa indonesio usando la misma infraestructura de traducción que ahora usa el panel
- [ ] Ninguna regresión en el tiempo de carga (actualmente rápido; no lo infles con bibliotecas de imágenes — `html2canvas` es la única dependencia pesada nueva)

## 6. No objetivos

- **Sin modal selector de público ni sistema de pestañas** ("¿Eres madre, docente o funcionario?"). Es artificioso. Estructura la página para que cada público encuentre su sección escaneando, no identificándose por adelantado.
- **Sin e-commerce.** "Get involved with sensors" es por ahora una inscripción a taller, no una compra de kit. Diseña la CTA para que pueda cambiar a un flujo de compra más adelante sin reescribir la página, pero no construyas el flujo de compra todavía.
- **Sin eliminar el contenido editorial de metodología.** Muévelo, condénsalo, pero no lo pierdas — es lo que da credibilidad a la campaña, sobre todo con el público de funcionarios. La sección "Local lead, credited methodology" pasa a formar parte del bloque de responsables de políticas.
- **Sin reemplazar la profundidad analítica del panel en la página de inicio.** El inicio muestra resúmenes y la correlación más llamativa; el panel sigue siendo el lugar para el análisis serio. No intentes convertir la página de inicio en un segundo panel.
- **Sin nuevo framework.** La misma restricción que el informe del panel — vanilla JS, sitio estático, sin React/Vue/etc.
- **Sin login ni estado por usuario en la página de inicio.** El inicio es de lectura pública, totalmente cacheable, sin datos por visitante más allá de la cookie/localStorage de localidad para "recordar mi barrio".

## 7. Dependencias e incógnitas

- **Flujo de permiso de geolocalización.** La mayoría de los visitantes lo denegará en la primera solicitud. Ten un repliegue sensato ("Agregado de toda Bali · elige tu zona abajo") y una UX de solicitud clara y no insistente.
- **Límites de las localidades.** El panel usa una lista `BALI_LOCALITIES` (en `reports/murmurations_adapter.py`) — reutilízala para el desplegable de localidad de la página de inicio. Si hay que añadir una localidad nueva, hazlo en un solo lugar e impórtala en todas partes.
- **Destino de inscripción al taller.** Decide antes de empezar la Fase 1: formulario de Airtable, Tally, un Formspree sencillo o un endpoint personalizado. Recomendación: Airtable para coincidir con la infraestructura de la encuesta.
- **Contenido del plan de clase.** v1 puede lanzarse con un PDF de una página que solo muestre "compara la lectura de PM2.5 de las últimas 24 h de tu escuela con la directriz diaria de la OMS y con una escuela de referencia en Barcelona a través de la red global de Smart Citizen". No necesita ser elaborado; necesita existir. El socio educador puede refinarlo más adelante.
- **Curación de la correlación diaria.** Hasta que el motor de correlación del panel elija automáticamente la historia del día, decide quién en Fab Lab Bali la elige y la escribe a mano cada día, y dónde vive el JSON. Se sugiere `data/daily_story.json`, actualizado por la misma vía de administración que los reportes.
- **Formato de la URL de compartir de WhatsApp en iOS Safari** — a veces inestable. Pruébalo en dispositivos reales, repliega a la API `navigator.share()` donde esté disponible.

## 8. Cómo empezar

1. Crea una rama de trabajo: `git checkout -b home-v2`
2. Lee [`index.html`](../index.html) de principio a fin. Identifica qué se queda, qué se mueve, qué es nuevo. Toma notas — el archivo tiene 1234 líneas y la reestructuración es el grueso del trabajo, no los componentes nuevos.
3. Lee este informe más [`PLATFORM_REVISION.md`](PLATFORM_REVISION.md) para que la revisión de la página de inicio quede coherente con el trabajo del panel que acaba de lanzarse.
4. Empieza con la Fase 1 (hero + CTA). Lánzala antes de tocar las secciones por público; mejora visible inmediata, bajo riesgo de regresión.
5. PR a `main`. GitHub Pages recoge los cambios automáticamente.

## 9. Cuando esto esté hecho

Actualiza este informe con un encabezado "Status: complete" y un resumen de un párrafo de lo que se concretó. Anota cualquier desviación del informe (una plantilla de tarjeta que no funcionó, una fase que necesitó replantear su alcance, un supuesto que resultó equivocado). El `REPLICATION.md` de la campaña hará referencia a esto como la versión de la página de inicio que otros capítulos de Fab City bifurcan — la exactitud importa.

Si el mecanismo de tarjetas compartibles resulta impulsar de verdad la interacción (lo cual sabremos por la analítica de referidos en el mes posterior al lanzamiento), habría que avisar al equipo de Fab Lab Barcelona — esto podría convertirse en un patrón que quieran llevar de vuelta a la plataforma original de Smart Citizen.

## 10. Contacto

- Líder de la campaña: Tomas Diez · `tomas@fab.city`
- Responsable del componente de reportes: equipo de Fab Lab Bali · `fablabbali@gmail.com`
- Fab Lab Barcelona (equipo de la plataforma Smart Citizen): `info@smartcitizen.me`
