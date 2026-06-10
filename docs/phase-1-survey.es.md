[English](phase-1-survey.md) · [Bahasa Indonesia](phase-1-survey.id.md) · **Español**

# Fase 1 — Encuesta sobre asuntos de interés

La guía de diseño, metodología y operación para la encuesta comunitaria de la Fase 1 de una campaña Making Sense [lugar]. Documenta la encuesta de Bali en marcha como diseño de referencia, con mejoras propuestas para la próxima iteración.

> **Formulario activo**: [airtable.com/appwQPP3ywSp4uu25/pag1mi3F086XPIlBy/form](https://airtable.com/appwQPP3ywSp4uu25/pag1mi3F086XPIlBy/form)
> **Base**: `appwQPP3ywSp4uu25` · Tabla: `Matters of Concern`

---

## Por qué una encuesta de Fase 1

Making Sense [lugar] no empieza desplegando sensores ni escribiendo un comunicado de prensa sobre la calidad del aire. Empieza preguntándole a los residentes qué problemas ambientales notan *ellos* en su vida diaria. Este punto de partida importa más de lo que parece.

El linaje metodológico es **[Making Sense](https://making-sense.eu/)** (EU Horizon 2020, 2015–2017), que adaptó el marco de los "matters of concern" de Bruno Latour a un protocolo participativo de citizen-sensing. La distinción central es entre los *matters of fact* (lo que mide la ciencia — PM2.5, dB, ppm) y los *matters of concern* (lo que de verdad preocupa a la gente — el humo que los despierta, el agua que sabe raro, el ruido que hace llorar a sus hijos).

Una campaña de sensado que empieza por los matters of fact construye un instrumento. Una campaña de sensado que empieza por los matters of concern construye una comunidad. La primera es una herramienta. La segunda tiene legitimidad política y la autoridad para cambiar algo de verdad.

La Fase 1 produce tres cosas:

1. **Un retrato de la atención que definen los residentes** — qué preocupaciones surgen, dónde, a quién afectan, qué evidencia ya existe
2. **Prioridades auténticas para la Fase 2** — qué barrios sensar primero, qué categorías debe destacar el bot de reportes, qué organizaciones aliadas invitar
3. **Una base ciudadana** — una lista de residentes que participaron y quieren involucrarse más (alojar un sensor, enviar reportes, traducir, asistir a talleres)

Sáltate la Fase 1 y habrás invertido el orden: les estás diciendo a los residentes qué deberían importarles según lo que es fácil de medir. Eso es un proyecto de investigación, no una campaña comunitaria.

---

## Principio de diseño: una fila = una preocupación

La encuesta de Bali está estructurada de modo que **un envío de formulario representa una preocupación**, no un encuestado. Un residente con tres preocupaciones ambientales envía el formulario tres veces — una por cada preocupación. Cada fila en Airtable captura la narrativa completa de esa preocupación específica: qué es, dónde, a quién afecta, qué evidencia existe, qué cambiaría si se hiciera visible.

Es una decisión deliberada con tres beneficios:

- **Más detalle por preocupación** del que cabría en una grilla de selección múltiple
- **El análisis por preocupación es natural** — agrupa por categoría, por ubicación o por "más afectados" sin desempaquetar datos anidados
- **Los encuestados que solo se preocupan por un tema pueden enviar rápido**; quienes tienen varios no se ven forzados a una única respuesta limitada

El costo es que los encuestados que envían varias preocupaciones ingresan su información identificativa (nombre, correo, etc.) varias veces. La sección de contacto opcional lo mantiene breve, y de todos modos la mayoría de los encuestados son anónimos.

---

## La encuesta actual de Bali

### Campos, en orden del formulario

| # | Campo | Tipo | Obligatorio | Propósito |
|---|---|---|---|---|
| 1 | **Concern** | Texto de una línea | Sí | Resumen de una línea — ¿cuál es el problema? Se convierte en el identificador principal de la fila. |
| 2 | **Categories** | Selección múltiple | Sí | A qué categoría o categorías ambientales corresponde esto |
| 3 | **Description** | Texto largo | Opcional | La narrativa — qué observaste en concreto, cuándo, qué aspecto/sonido/olor tiene, con tus propias palabras |
| 4 | **Location** | Texto largo | Opcional | Dónde ocurre — barrio, calle, playa, escuela, hora del día si es relevante |
| 5 | **Most affected** | Selección múltiple | Opcional | Quién es el más afectado por este problema |
| 6 | **Existing evidence** | Texto largo | Opcional | Qué evidencia ya existe — observaciones propias, reportes de otros, noticias, datos oficiales |
| 7 | **What would change** | Texto largo | Opcional | Teoría del cambio — qué cambiaría si los datos hicieran esto visible, y a quién deberían llegar los datos |
| 8 | **Willing to participate** | Selección múltiple | Opcional | Cómo quiere involucrarse más el encuestado (anfitrión de sensor, reportero, talleres, traducción, difusión, solo informado, declina) |
| 9 | **Preferred languages** | Selección múltiple | Opcional | Qué idiomas debería admitir la campaña |
| 10 | **Name** | Texto de una línea | Opcional | Déjalo en blanco para quedar anónimo |
| 11 | **Email** | Correo | Opcional | Solo si quieres que te contacten sobre los próximos pasos |
| 12 | **Phone / WhatsApp** | Teléfono | Opcional | Solo se usa si el encuestado pide seguimiento |
| 13 | **Affiliation** | Texto de una línea | Opcional | Escuela, ONG, fab lab, asociación vecinal, organización |

Campos solo internos (no están en el formulario, los completa el equipo tras el envío):

- **Status** — estado de revisión: New → Reviewed → Contacted → Workshop invited → Closed / archived (o Spam / invalid)
- **Submitted at** — automático desde el formulario
- **Internal notes** — notas de triaje, acciones de seguimiento, asignación de contacto

### Opciones de selección tal como están desplegadas (Bali)

**Categories** — Burning waste · Air quality · Water · Noise · Heat & humidity · Plastic & solid waste · Soil & agriculture · Light pollution · Other

**Most affected** — Me personally · My family · Children / students · Elderly / vulnerable people · Workers · Neighbors / community · Animals / wildlife · Visitors / tourists · Other

**Willing to participate** — Host a sensor · Share reports via the bot · Attend workshops · Translate / localize · Connect us to my school / org · Just keep me informed · Prefer not to participate further

**Preferred languages** — Bahasa Indonesia · English · Bahasa Bali · Other

**Status (internal)** — New · Reviewed · Contacted · Workshop invited · Closed / archived · Spam / invalid

---

## Justificación — por qué estos campos, en este orden

El formulario está ordenado para reducir el abandono: las preguntas fáciles / más importantes van primero, las opcionales / personales van al final. Un residente que solo completa los tres primeros campos (Concern, Categories, Description) igual le da a la campaña datos útiles.

- **Concern primero** — un resumen de una línea obliga a los encuestados a articular qué están reportando antes de entrar en detalles. Funciona como dato y como autoaclaración a la vez.
- **Categories segundo** — taxonomía estructurada para el análisis posterior. La opción "Other" la mantiene abierta.
- **Description, Location, Most affected** — el triángulo *qué / dónde / quién*. Todos opcionales individualmente, así que las respuestas parciales siguen siendo útiles.
- **Existing evidence** — una señal de respeto. La pregunta da por hecho que los residentes ya saben cosas; la campaña no parte de cero. Esto suele producir el texto más rico, con gente que nombra fuentes, fechas y reportes previos.
- **What would change** — el detonante de la teoría del cambio. Cabe destacar que *no hay un catálogo estructurado de intervenciones* — es intencional. Los residentes nos dicen con sus propias palabras qué creen que ayudaría y a quién deberían llegar los datos. Las opciones estructuradas los condicionarían hacia nuestras suposiciones previas.
- **Willing to participate** — la rampa de entrada a la Fase 2. Lo bastante granular para encajar con distintos niveles de compromiso.
- **Preferred languages** — informa tanto las prioridades de traducción del bot como las decisiones sobre canales de difusión.
- **Campos de contacto al final** — opcionales, nunca obligatorios, nunca razonable exigirlos en una encuesta de "qué te preocupa".

### Lo que a propósito no se pregunta

- **Demografía (edad, género)** — el piloto de Bali los probó en un borrador anterior y los descartó tras ver poco impacto en la finalización. Podrían volver como opcionales una vez que el volumen de respuestas justifique la estratificación.
- **Tolerancias específicas de PM2.5 / dB** — eso son matters of fact, no matters of concern. Corresponde a la instrumentación de la Fase 2, no a la encuesta de la Fase 1.
- **Opción múltiple de "qué ayudaría"** — condicionaría las respuestas. En su lugar, texto libre.

---

## Adiciones de campos — qué hay ahora en la base activa

El 2026-05-12 se añadieron siete campos nuevos a la base activa de Bali. Existen en la tabla pero **AÚN NO se han añadido a la vista de formulario** — ese es un paso manual en el editor de formularios de Airtable, separado a propósito para que el equipo pueda revisar el orden de los campos y cualquier reformulación antes de exponerlos a los encuestados.

Campos nuevos:

| Campo | Tipo | Propósito |
|---|---|---|
| **Neighborhood** | Selección única | Selector estructurado de localidad que cubre Bukit (Uluwatu, Pecatu, Ungasan, Bingin, Balangan, Padang Padang, Jimbaran, Nusa Dua, Kutuh, Benoa) más el resto de Bali. Reemplaza el Location no estructurado para el análisis; Location queda como complemento de texto libre. |
| **How long have you lived here** | Selección única | <1año / 1–5años / 5–10años / >10años / visitante / prefiero no decir. Distingue la percepción del recién llegado de la del residente de larga data. |
| **How did you hear about us** | Selección múltiple | Amistad, escuela, banjar, Instagram, WhatsApp, Facebook, organización aliada, prensa, póster, lo encontré directamente, otro. Retroalimentación sobre canales de difusión. |
| **How often does this happen** | Selección única | Diario / semanal / mensual / estacional / único / no sé. Lente de frecuencia. |
| **When is it worst** | Selección múltiple | Desde la madrugada hasta la noche, más fin de semana/día laboral/todo el día. Crucial para las decisiones de colocación de sensores de la Fase 2. |
| **What you've tried** | Texto largo | Qué han hecho los residentes personalmente — hablar con vecinos, reportar, unirse a un grupo, cambiar la rutina, comprar equipo. Saca a la luz la sabiduría comunitaria que `Existing evidence` confundía con documentación. |
| **Outcome of what you tried** | Selección única | Ayudó / en parte / no / es muy pronto / no lo he intentado / no aplica. Complemento estructurado del texto libre. |

**Próximo paso (manual)**: abre la vista de formulario de Airtable en el editor de la base y arrastra estos campos al formulario en este orden recomendado:

- Después de `Location`: inserta `Neighborhood` (para que los encuestados reciban el selector estructurado justo donde ya están pensando en el lugar)
- Después de `Categories`: inserta `How often does this happen` y `When is it worst`
- Después de `Existing evidence`: inserta `What you've tried` y `Outcome of what you tried`
- Cerca del final, después de `Affiliation`: inserta `How long have you lived here` y `How did you hear about us`

Los siete deben ser **opcionales** en la vista de formulario — ninguno obligatorio. Los únicos campos obligatorios del formulario siguen siendo Concern y Categories.

### Cosas que a propósito NO se añadieron

- Campos demográficos (edad, género, ingresos del hogar) — aumentan la fricción sin valor analítico a escala piloto.
- Deslizadores de "Severidad 1–10" para la preocupación — cuantificar una severidad subjetiva añade ruido, no señal. La narrativa del residente es más útil.
- Pin en el mapa mediante un widget de terceros — posible vía integración con Softr / Stacker, aplazado hasta que el volumen de respuestas justifique el costo de la integración.

---

## Replicación — esquema para hacer fork de la encuesta

Para otro capítulo de Fab City que haga fork de la encuesta de Bali para su propia biorregión, este es el esquema de Airtable que vas a replicar. El ID de la base es por despliegue; la estructura es compartida.

### Base: `Making Sense [Tu Lugar] · Matters of Concern`

### Tabla: `Matters of Concern` — una fila por preocupación enviada

Replica la lista de campos de arriba. Los campos estructurales (Concern, Categories, Description, Location, Most affected, Existing evidence, What would change, Willing to participate, Preferred languages, Name, Email, Phone, Affiliation, Status, Submitted at, Internal notes) se trasladan directamente.

Lo que personalizas para tu biorregión:

- **Categories** — adapta la lista a tu contexto. La de Bali incluye "Heat & humidity" (relevante en los trópicos) y "Soil & agriculture" (arrozales, plantaciones). Barcelona podría quitarlas y añadir "Heritage / built environment" o "Heatwaves" (otra urgencia). Yucatán podría añadir "Cenote contamination." Conserva "Other" siempre.
- **Most affected** — adapta las categorías demográficas. "Visitors / tourists" importa en Bali porque el turismo es una fuerza económica y ambiental mayor; menos aplicable en ciudades no turísticas. "Workers" normalmente debería quedarse (trabajadores informales, vendedores de mercado).
- **Willing to participate** — conserva la estructura. Adapta la redacción a las convenciones locales ("Connect us to my banjar" → "Connect us to my junta vecinal", etc.).
- **Preferred languages** — tu(s) idioma(s) local(es) en lugar de Bahasa Indonesia + Bahasa Bali. English es convencional como opción secundaria.

### Replicar el formulario activo

La vista de formulario integrada de Airtable es el camino más simple:

1. Crea la base + tabla con el esquema de arriba
2. Crea una vista de Formulario, arrastra los campos en el orden que muestra la tabla de orden del formulario
3. Marca Concern y Categories como obligatorios; todo lo demás opcional
4. Configura el mensaje de confirmación de envío del formulario con la voz del Fab Lab anfitrión
5. Incrústalo en el sitio de tu campaña, o comparte la URL del formulario directamente en la difusión

### Prellenado por barrio (opcional)

Para difusión específica por barrio, agrega un parámetro de consulta a la URL del formulario para prellenar el campo Location o Neighborhood:

```
[your-form-url]?prefill_Neighborhood=Eixample
[your-form-url]?prefill_Neighborhood=Gràcia
```

Envía la URL prellenada a los canales de difusión específicos del barrio (grupos de WhatsApp del banjar, listas de padres de la escuela, etc.) — menos campos que llenar, mejores tasas de finalización.

---

## Manual de difusión

El diseño de la encuesta no importa si nadie la completa. La difusión de la Fase 1 es el trabajo que sostiene toda la campaña.

### Mezcla de canales

Una mezcla de difusión que funciona para una biorregión de 50.000–500.000 personas:

| Canal | Alcance | Esfuerzo | Conversión |
|---|---|---|---|
| Canales que ya tiene el Fab Lab anfitrión | medio | bajo | alta |
| Escuelas aliadas (grupos de padres, profesorado) | alto | medio | alta |
| Consejos vecinales / banjars / juntas | medio | medio-alto | muy alta |
| Grupos comunitarios de WhatsApp (los locales que ya existen) | alto | medio | media |
| Instagram / redes sociales locales | alto | bajo | baja |
| Pósters en tiendas, mercados, tableros comunitarios | medio | medio | baja (pero construye legitimidad) |
| Prensa / radio local | alto | alto | baja (pero construye legitimidad) |
| Difusión directa en persona (mercados, eventos) | bajo | alto | muy alta |

Los canales de alta conversión son los lentos que construyen confianza. Los canales de alto alcance son débiles en conversión. Una campaña que solo hace redes sociales obtendrá respuestas ruidosas de una demografía estrecha; una que solo hace presencia en persona obtendrá respuestas ricas de poca gente. Combina ambos y dale más peso a lo que tu Fab Lab anfitrión hace bien.

### Cronograma

Un calendario de difusión de la Fase 1 viable:

- **Semana –2**: diseña la encuesta, tradúcela, configura Airtable, crea el póster + los recursos para redes
- **Semana –1**: informa a los aliados, redacta los mensajes de difusión, prepara el seguimiento interno
- **Semana 1**: lanzamiento suave a través del Fab Lab + los aliados más cercanos. Meta: ~30 respuestas para probar el formulario
- **Semana 2**: revisa el formulario si hace falta según la retroalimentación temprana (erratas, lógica rota, secciones con baja finalización), luego **lanzamiento completo**
- **Semanas 2–6**: difusión activa por todos los canales, sincronización semanal con aliados, comparte hallazgos tempranos en público para mostrar que la encuesta se está leyendo
- **Semana 6**: cierre suave — la campaña reduce la difusión activa pero mantiene el formulario abierto
- **Semana 8**: cierre definitivo — conteo final de respuestas, comienza el análisis

Total: 8 semanas de recolección activa, más 2 semanas de preparación antes y 2–4 semanas de análisis + publicación después.

### Traducción

El texto de la encuesta de la Fase 1 debe ser revisado por **hablantes nativos de tu biorregión** antes de hacerse público. Las preguntas que escribiste en inglés perderán matices, ganarán implicaciones accidentales y se perderán encuadres específicos del lugar al traducirse. Presupuesta 1–2 semanas para el ciclo de revisión de la traducción, no 1 día.

Para Bali: Bahasa Indonesia primario, English secundario. Bahasa Bali se ofrece como preferencia de idioma, pero el formulario en sí está actualmente en Bahasa + English — añadir una versión balinesa del formulario es una mejora a futuro.

Para Barcelona: Catalan primario, Spanish secundario, English opcional. Ten en cuenta que un texto de encuesta que "se siente bien" en español puede leerse como excluyente en barrios donde predomina el catalán (Gràcia, partes de Eixample) — y viceversa.

### Incentivos

Tres enfoques que funcionan:

1. **Sin incentivo, planteado como contribución cívica.** Funciona en comunidades densas con una cultura cívica activa. Honesto sobre lo que pide la campaña.
2. **Agradecimiento opcional en el formulario** — una descarga digital (un PDF del panel de calidad del aire, una guía de los problemas ambientales de la ciudad) enviada automáticamente al enviar. Bajo costo, señala reciprocidad.
3. **Agradecimiento físico en eventos** — en los mercados, escuelas o sitios aliados donde recolectas en persona, una botellita, una calcomanía o un artículo con la marca.

Evita pagar por respuestas. Inclina la mezcla demográfica hacia gente que necesitaba el dinero en lugar de gente que se preocupaba por los temas, y plantea la relación equivocada para la Fase 2.

### Plantilla de texto de difusión

El recurso de difusión más usado será un párrafo corto que adaptas para cada canal. Plantilla:

> 🌴 *Making Sense [Lugar]* — la campaña del Fab Lab [Ciudad] sobre los problemas ambientales de nuestros barrios.
>
> Le estamos preguntando a los residentes qué problemas ambientales afectan su vida diaria — aire, agua, ruido, residuos, lo que sea. Esto es la *Fase 1*: construir un retrato de lo que de verdad notan los vecinos, antes de desplegar ningún sensor. Tu aporte define dónde nos enfocamos después.
>
> 🔒 Anónimo salvo que elijas que te demos seguimiento. ~5 minutos por preocupación.
>
> 📝 [enlace a la encuesta]
>
> *Llevado adelante por el Fab Lab [Ciudad] · Parte de [Fab City [Ciudad]] · Hecho por vecinos, para vecinos.*

Traduce, adapta, publica.

---

## Análisis y publicación

La Fase 1 queda incompleta si no se cierra el círculo. Los residentes que participaron necesitan ver que la campaña lee su aporte. No hacerlo — recolectar y desaparecer — es el modo de fallo más común de las encuestas comunitarias.

### Qué analizar

Tres capas:

1. **El catálogo de preocupaciones** — cantidad de preocupaciones por categoría, visualizada como un gráfico de barras horizontal en la página pública de resumen. Como la encuesta es de una fila por preocupación, esto es una suma directa en lugar de desempaquetar una selección múltiple.
2. **La geografía** — qué ubicaciones (extraídas del texto libre de Location, o de Neighborhood una vez añadido) se repiten. Un mapa de calor simple o una lista anotada. Cruza con Categories para ver patrones de categoría × ubicación.
3. **La narrativa** — citas seleccionadas de Description, Existing evidence y What would change. Editadas para acortarlas y darles claridad, anonimizadas con un estilo de atribución del tipo "*Residente, [barrio], [antigüedad]*". El artefacto más potente para la prensa, las políticas y las conversaciones comunitarias.

Análisis adicional opcional una vez que tengas más de 100 preocupaciones:

- Tablas cruzadas (Categories × Most affected — ¿"Burning waste" afecta más a menudo a niños, animales o personas mayores?)
- Brechas de acción (una vez añadido el campo `What you've tried` — qué intentaron los residentes vs qué funcionó, sacando a la luz dónde hace falta acción colectiva)
- Grupos de teoría del cambio (codificación cualitativa del texto libre de `What would change` — ¿la comunidad quiere fiscalización, organización, información o infraestructura?)

### Qué publicar

La página de resultados de la Fase 1 en el sitio de tu campaña debería incluir:

- Número de preocupaciones enviadas, número de encuestados únicos (si se conoce), fechas de recolección
- La visualización del catálogo de preocupaciones
- El patrón geográfico
- 5–10 citas seleccionadas de residentes
- Una declaración clara de qué hará la Fase 2 en respuesta

El último punto es crucial. "Escuchamos que X es la principal preocupación en [barrio], así que la Fase 2 desplegará sensores allí, priorizará las categorías Z en el bot de reportes, trabajará con [aliado] en [acción]." Eso es cerrar el círculo.

### Devolver los resultados a los encuestados

Un correo breve a los encuestados que optaron por el seguimiento, que resuma los hallazgos y los invite a la Fase 2. Haz que este correo sea genuinamente interesante — no una plantilla corporativa — y que venga de una persona con nombre del Fab Lab anfitrión.

---

## Iteración — qué aprenderemos en Bali

La encuesta de la Fase 1 de Bali está en su fase más temprana a fecha 2026-05-12 — el formulario está activo, el esquema se ha ampliado con los campos nuevos de arriba, y la difusión activa está por empezar. Esta sección se irá completando a medida que lleguen respuestas reales.

Lo que vigilamos, con base en la literatura previa de citizen-sensing y el proyecto Making Sense:

- **Longitud y calidad de las respuestas de texto libre.** La hipótesis es que `What would change` y `Existing evidence` recibirán las respuestas más largas y reflexivas — los residentes tienen teorías del cambio y tienen conocimiento local; la encuesta es uno de los pocos lugares que lo pregunta. Si la finalización es alta en estos campos, el diseño funciona.
- **Tasa de opt-in para la Fase 2.** ¿Qué porcentaje marca al menos una opción en `Willing to participate`? La expectativa ingenua de los proyectos típicos de civic-tech es 15–30%; si es mayor, el encuadre de la campaña resuena de forma inusual; si es menor, algo en el mensaje está fallando.
- **Mezcla de categorías.** ¿Qué Categories se acumulan más rápido? En Bali esperamos que Burning waste, Plastic & solid waste y Air quality vayan a la cabeza. Las sorpresas aquí moldean directamente las prioridades de sensores de la Fase 2.
- **Envíos anónimos vs identificados.** ¿Qué proporción se salta del todo los campos de contacto? Esto indica el nivel de confianza en el formulario y en la institución anfitriona.
- **Distribución geográfica.** Una vez que `Neighborhood` se añada al formulario, ¿qué ubicaciones bbox reportan qué categorías? Los patrones aquí guían la colocación de sensores y el enfoque de la difusión.

Esta lista se reemplazará por lecciones concretas a medida que la campaña madure. Se agradecen PRs a este documento con observaciones de otros Fab Labs.

---

## Hacer fork para tu ciudad — pasos concretos

1. **Lee este documento completo.** Luego mira el [formulario activo de Bali](https://airtable.com/appwQPP3ywSp4uu25/pag1mi3F086XPIlBy/form) para sentir cómo se vive el diseño como encuestado.
2. **Crea una nueva base de Airtable** en tu espacio de trabajo. Replica el esquema de la tabla `Matters of Concern` (15 campos, incluidos los 3 solo internos) según la tabla de arriba.
3. **Adapta las opciones de selección** a tu biorregión. Categories, Most affected, Willing to participate (redacción para los consejos locales), Preferred languages.
4. **Traduce las descripciones de los campos y el texto del formulario** a tu(s) idioma(s) local(es). Revisión por hablantes nativos antes del lanzamiento público.
5. **Adapta el mensaje de envío del formulario** para que se sienta local. ("Terima kasih!" en Bali → "Gràcies!" en Barcelona → etc.)
6. **Diseña tu mezcla de difusión** — canales, aliados, cronograma. Verifica que tenga sentido con el Fab Lab anfitrión y la persona líder de la campaña antes de lanzar.
7. **Lanzamiento suave** con ~10–30 respuestas de vecinos de confianza. Arregla los problemas del formulario antes de abrirlo a todos.
8. **Lanzamiento completo** a través de tu mezcla de canales. Periodo activo de 6–8 semanas.
9. **Analiza y publica** dentro de las 4 semanas tras el cierre. Deja claros los compromisos de la Fase 2.

El sentido de la Fase 1 es darle base a la Fase 2. No la apresures, y no dejes que se convierta en un estado permanente — la encuesta es una herramienta, no un fin.

---

## Licencia

Este documento y el diseño de las preguntas: **CC-BY-SA 4.0**. Haz un fork, adáptalo a tu biorregión, comparte lo que aprendas.

---

Parte de [Making Sense Bali](../README.md). Para el contexto completo de la campaña consulta el [README principal](../README.md). Para la replicación consulta [REPLICATION.md](../REPLICATION.md).
