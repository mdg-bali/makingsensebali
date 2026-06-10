[English](README.md) · [Bahasa Indonesia](README.id.md) · **Español**

# DIY node — herramientas de taller

Pequeñas utilidades para trabajar con los kits DIY node durante la puesta en marcha,
el burn-in, la calibración y el onboarding. No son necesarias para el funcionamiento normal
una vez que el kit está en marcha; el firmware de producción publica directamente en
Smart Citizen.

## `register_device.py` — saltarse el flujo de onboarding

Registra un DIY node personalizado en la plataforma Smart Citizen a través de la API,
sin pasar por el flujo de onboarding web ni su correspondiente
barrera de activación. Esta es la vía que usa la herramienta SCK oficial para
hardware personalizado (ver `fablabbcn/smartcitizen-tools` → `sck.py:register()`).

**Cuándo usarlo:**

- Estás desplegando un node personalizado (no un SCK de fábrica) y no
  quieres esperar la aprobación del admin en el flujo de onboarding web.
- Estás dando un taller donde cada participante necesita su propio
  dispositivo registrado en minutos, no en días.
- Estás construyendo automatización en torno al aprovisionamiento de dispositivos.

**Configuración (una sola vez):**

```bash
pip3 install requests
```

Luego obtén tu token de API de usuario de SC en `smartcitizen.me → My Profile →
API → personal access token`. Pásalo con `--bearer` o establécelo
en tu entorno como `SC_BEARER`.

**Ejecutar:**

```bash
# Interactive
python3 register_device.py

# Non-interactive — Plus kit (BME680 + HM3301)
export SC_BEARER=your_user_api_token
python3 register_device.py \
    --name "Bali DIY Node — Office" \
    --lat -8.65 --lon 115.21 --exposure indoor --kit plus

# Basic kit (BME680 only) — only 4 sensors to attach
python3 register_device.py --kit basic ...
```

La salida imprime el ID del dispositivo, la URL, el token MQTT, el topic y una lista
de sensores adaptada a la variante del kit (4 sensores para Basic, 7 para Plus).
Tras el registro, abre la URL del dispositivo en smartcitizen.me, añade los
sensores listados a través de la UI si no se adjuntan automáticamente, copia los
IDs de sensor en la configuración del firmware y flashea.

## `show_sensors.py` — obtener IDs de sensor listos para pegar

Una vez que un dispositivo tiene sensores adjuntos en la plataforma SC, este script
obtiene el JSON del dispositivo, imprime una tabla limpia de los sensores adjuntos
con nombres e IDs, y emite un bloque de configuración listo para el firmware que puedes
pegar directamente en `diy_node.ino`. Mapea automáticamente los nombres de sensor de SC a las
constantes `SC_ID_*` correspondientes (Temperature, Humidity, Pressure, Gas
resistance, PM1, PM2.5, PM10).

**Ejecutar:**

```bash
pip3 install requests       # one-time
python3 show_sensors.py 19651
```

Salida para un dispositivo sin sensores todavía (el estado típico justo
después del registro por API, antes de que el equipo de la plataforma adjunte un
blueprint de hardware):

```
Smart Citizen device 19651 — Bali DIY Node — Office
  state : never_published
  last  : never
  count : 0 sensor(s) attached
  ...

No sensors attached yet. (Ping the SC team with the device URL...)
```

Salida una vez que los sensores están adjuntos:

```
  ID      Name                                Unit        Maps to
  ─────   ──────────────────────────────      ─────       ─────────────────
   14     Temperature                         °C          SC_ID_TEMP
   56     Humidity                            %           SC_ID_HUM
   58     Barometric pressure                 hPa         SC_ID_PRESSURE
   ...

Paste into diy_node.ino — replace the SC_ID_* lines in the CONFIGURATION block:

  const int SC_ID_TEMP       = 14    ;  // °C       — BME680 temperature
  const int SC_ID_HUM        = 56    ;  // %RH      — BME680 humidity
  ...
```

Úsalo cada vez que cambie la configuración del lado de la plataforma (sensor
añadido/eliminado, blueprint reasignado) — vuelve a obtener y vuelve a pegar.

## `find_sensor_ids.py` — encontrar IDs globales de sensor de SC bajo los que publicar

La ingesta MQTT de la plataforma Smart Citizen crea las asociaciones
de sensor de un dispositivo automáticamente a partir de los IDs del payload
de publicación — pero esos IDs deben provenir del catálogo global de
sensores de la plataforma (`/v0/sensors`), no inventarse localmente. Esta herramienta
obtiene el catálogo y te ayuda a encontrar los IDs correctos para las
métricas del kit DIY.

**Ejecutar:**

```bash
pip3 install requests       # one-time
python3 find_sensor_ids.py
```

El modo por defecto busca las siete métricas del kit Plus (Temperature,
Humidity, Pressure, Gas resistance, PM1, PM2.5, PM10), prefiriendo las
entradas específicas del BME680 donde existan en el catálogo.

Para búsquedas arbitrarias:

```bash
python3 find_sensor_ids.py BME680
python3 find_sensor_ids.py PM Plantower
```

La salida muestra cada coincidencia con `id  name  [unit]` para que puedas elegir
la entrada más específica y pegar su ID en `diy_node.ino`.

**Flujo de trabajo (tras la relectura de Oscar):**

1. `register_device.py` → registro del dispositivo creado en SC (✓)
2. **`find_sensor_ids.py`** → encuentra los IDs globales para las métricas de tu kit
3. Pega los IDs en el bloque CONFIGURATION de `diy_node.ino`
4. Flashea → el dispositivo publica → la plataforma crea automáticamente los mapeos dispositivo-sensor
5. `show_sensors.py <device_id>` → verifica que los sensores ahora aparecen en el registro del dispositivo

## `log_serial.py` — registrador USB serial → CSV

Lee la salida Serial del sketch de prueba (o del sketch de producción) por
USB y añade filas con marca de tiempo a un CSV. Funciona tanto con Basic
(solo BME680) como con Plus (BME680 + HM3301) — las columnas PM se dejan
vacías cuando el HM3301 no está presente.

**Cuándo usarlo:**

- Caracterización de burn-in — captura 24–48 h de lecturas para ver
  cómo el sensor de gas del BME680 se estabiliza desde su estado inicial de baja resistencia.
- Verificación de taller — da a los participantes un CSV de su primera
  hora de datos para que puedan graficarlo y ver el sensor funcionando.
- Sprints de calibración — cuando un DIY Plus se coubica con un
  SCK oficial para derivar un factor de corrección, registra ambos con marca de tiempo
  para alinear las series más tarde.

**Configuración (una sola vez):**

```bash
pip3 install pyserial
```

**Ejecutar:**

```bash
# Autodetect port, write to readings_<timestamp>.csv in cwd
python3 log_serial.py

# Custom output path
python3 log_serial.py --out office_burnin.csv

# Specify port explicitly (use `ls /dev/cu.*` on macOS to find it)
python3 log_serial.py --port /dev/cu.usbmodem1101
```

Ctrl-C para detener. El CSV se vacía de forma limpia al salir.

**Columnas del CSV:**

| Columna | Unidad | Fuente |
|---|---|---|
| `timestamp_iso` | UTC ISO 8601 | Reloj del Mac en el momento de la lectura |
| `t_c` | °C | BME680 |
| `rh_pct` | %RH | BME680 |
| `p_hpa` | hPa | BME680 |
| `gas_kohm` | kΩ | BME680 (indicador de VOC) |
| `pm1` | µg/m³ | HM3301 (vacío para el kit Basic) |
| `pm2_5` | µg/m³ | HM3301 (vacío para el kit Basic) |
| `pm10` | µg/m³ | HM3301 (vacío para el kit Basic) |

**Graficado:**

Mete el CSV en tu herramienta favorita — Numbers, Excel, Google Sheets,
o:

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("readings_20260520_184530.csv", parse_dates=["timestamp_iso"])
df.set_index("timestamp_iso").plot(subplots=True, figsize=(12, 10))
plt.show()
```

Para las corridas de burn-in, la curva de resistencia de gas es la vista más interesante
— deberías verla subir desde unos pocos kΩ hasta decenas o cientos de
kΩ durante las primeras 24 horas, y luego asentarse en una línea base con pequeñas
oscilaciones diurnas ligadas a tu actividad de interior (cocinar, limpiar,
electrónica, ocupación).
