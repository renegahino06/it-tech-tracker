# it-tech-tracker
IT Technology Trends Report

Pipeline automático que cada día recopila noticias de tecnología, las filtra, clasifica y rankea, elige la noticia más relevante y genera contenido listo para publicar en LinkedIn y X, una infografía, un informe HTML y un video informativo de esa noticia. Todo se envía por correo.

## Qué genera

| Archivo | Descripción |
|---|---|
| `data/top_story.json` | Noticia más relevante del día y su contenido (título, por qué importa, recomendaciones). |
| `data/infographic.png` | Infografía de la noticia principal. |
| `data/report.html` | Informe HTML con todas las noticias clasificadas. |
| `data/news_report.json` | Noticias clasificadas en formato JSON. |
| `data/narration.mp3` | Narración del video. |
| `data/video_<titulo>.mp4` | Video informativo; el nombre sale del título de la noticia. |

Estos archivos se generan en cada ejecución. El workflow los sube como artefacto (`it-tech-tracker-content-<run>`, 7 días de retención), y `narration.mp3` y `video_*.mp4` están en `.gitignore`.

El correo incluye el informe HTML, la infografía y el video como adjuntos, junto con el texto sugerido para LinkedIn y X.

## Flujo del pipeline

Definido en `src/main.py`:

1. **Collect** (`collector.py`): lee los feeds RSS de Hacker News, r/devops, r/artificial y The Hacker News.
2. **Filter** (`filtering.py`): conserva solo los títulos con palabras clave de tecnología (IA, seguridad, cloud, DevOps, etc.) y descarta los de humor, memes y autopromoción.
3. **Classify** (`classifier.py`): asigna categorías por palabras clave: `SECURITY`, `AI`, `DEVOPS`, `CLOUD`, `AUTOMATION`, `OTHER`.
4. **Summarize y textos sociales** (`summarizer.py`, `report_generator.py`): resumen y textos para LinkedIn y X.
5. **Ranking** (`ranking.py`): puntúa cada noticia y elige la principal (`select_top_story`).
6. **Contenido de la noticia** (`content_generator.py`): arma el paquete de la noticia principal.
7. **Infografía y video** (`infographic.py`, `video_generator.py`): generan los archivos de la noticia principal. Si alguno falla, el pipeline sigue y muestra un `WARN`.
8. **Informe y correo** (`exporter.py`, `report_generator.py`, `email_sender.py`): guardan el informe y lo envían.

No hay LLM en el flujo. Los textos, las recomendaciones y los ejemplos de código salen de reglas y bibliotecas fijas en el código.

## Tecnologías

- **Python 3.11** (en CI) y 3.13 (local).
- **feedparser**: lectura de RSS.
- **Pillow**: infografía y tarjetas del video.
- **edge-tts**: narración en español, sin API key.
- **ffmpeg** (con `libass`): render del video y subtítulos karaoke.
- **pygments**: resaltado de sintaxis en la escena de configuración.
- **GitHub Actions**: ejecución diaria (`cron: 0 13 * * *`, 07:00 hora de Ciudad de México) y manual con `workflow_dispatch`.
- **SMTP**: envío del correo (por defecto Gmail).

## Estructura del repositorio

```
.github/workflows/daily-report.yml   Workflow diario y manual
assets/avatar.png                    Avatar que aparece en el video
src/
  main.py                            Orquesta el pipeline
  collector.py, filtering.py,        Recolección, filtrado, clasificación,
  classifier.py, ranking.py          ranking
  summarizer.py, report_generator.py Resumen y textos sociales
  content_generator.py               Paquete de la noticia principal
  security_guide.py                  Biblioteca de tecnologías y pasos de
                                     mitigación (escenas de seguridad)
  video_generator.py                 Escenas, narración y render del video
  infographic.py                     Infografía
  exporter.py, storage.py            Guardado de resultados
  email_sender.py                    Envío del correo
data/                                Salidas generadas en cada ejecución
requirements.txt                     Dependencias de Python
```

## Escenas del video

`src/video_generator.py` arma las escenas a partir de la noticia principal:

1. **Título**: noticia y temas.
2. **¿Por qué importa?**: explicación breve.
3. **Configuración práctica**: comandos o YAML de ejemplo con resaltado de sintaxis, desde `CODE_EXAMPLES` según la categoría.
4. **Diagrama**: en ciberseguridad, el escenario de riesgo (exposición → software → versión sin parche → acceso no autorizado) con controles debajo de cada flecha. En el resto de categorías, un flujo general de la noticia.
5. **Pasos de mitigación**: solo en ciberseguridad. Usa `security_guide.py`: si la noticia menciona una tecnología conocida (OpenSSL, Log4j, OpenSSH, nginx, Docker, Kubernetes, Node.js, Python, Windows), muestra comandos específicos; si no, pasos genéricos.
6. **Recomendaciones** y **cierre** con la fuente.

Cada escena se narra con `edge-tts`. El avatar rebota mientras habla y los subtítulos se iluminan al ritmo de la voz.

Para cambiar ejemplos o tecnologías, edita `CODE_EXAMPLES` en `video_generator.py` o `TECH_GUIDES` en `security_guide.py`. Las palabras clave se comparan por palabra completa.

## Configurar secrets en GitHub para el envío de correos

Agrega los siguientes secrets en el repositorio de GitHub (Settings → Secrets and variables → Actions). Los nombres deben coincidir con los que usa el workflow:

- `EMAIL_USER`: dirección de correo que enviará el informe.
- `EMAIL_PASSWORD`: contraseña o token de aplicación del correo emisor.
- `EMAIL_TO`: dirección de correo destinataria.
- `SMTP_HOST`: servidor SMTP (por ejemplo `smtp.gmail.com`).
- `SMTP_PORT`: puerto SMTP (por ejemplo `587`).

`EMAIL_SENDER` (en lugar de `EMAIL_USER`) y `EMAIL_PASS` (en lugar de `EMAIL_PASSWORD`) también se aceptan en `email_sender.py`.

> Si usas Gmail, lo más probable es que necesites usar un App Password en vez de tu contraseña normal. Gmail suele rechazar el acceso SMTP cuando la cuenta tiene verificación en dos pasos o cuando no se usa un App Password.

Para Gmail, sigue estos pasos:

1. Activa la verificación en dos pasos en tu cuenta de Google.
2. Ve a `https://myaccount.google.com/security`.
3. En "Contraseñas de aplicaciones", crea una contraseña para "Correo" y "Otro (nombre personalizado)".
4. Copia el App Password y pégalo en el secret `EMAIL_PASS`.
5. Asegúrate de que `EMAIL_USER` sea tu correo completo, por ejemplo `tu_correo@gmail.com`.

Para Gmail, sigue estos pasos:

1. Activa la verificación en dos pasos en tu cuenta de Google.
2. Ve a `https://myaccount.google.com/security`.
3. En "Contraseñas de aplicaciones", crea una contraseña para "Correo" y "Otro (nombre personalizado)".
4. Copia el App Password y pégalo en el secret `EMAIL_PASSWORD`.
5. Asegúrate de que `EMAIL_USER` sea tu correo completo, por ejemplo `tu_correo@gmail.com`.

Opciones típicas para Gmail:

```env
EMAIL_USER=tu_correo@gmail.com
EMAIL_PASSWORD=tu_app_password_generado
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EMAIL_TO=destinatario@example.com
```

### Ejecutar diariamente desde GitHub Actions

El workflow `.github/workflows/daily-report.yml` se ejecuta todos los días a las 13:00 UTC (07:00 en Ciudad de México). También puede lanzarse a mano desde la pestaña **Actions** con "Run workflow", o desde la terminal con `gh workflow run daily-report.yml --ref <rama>` para probar una rama antes de fusionarla.

El workflow instala Python 3.11, las dependencias de `requirements.txt` y ffmpeg, ejecuta `src/main.py` y sube los archivos de `data/` como artefacto.

### Video informativo

El pipeline genera un video animado de la noticia principal. Las escenas, el diagrama y los pasos de mitigación se describen en la sección [Escenas del video](#escenas-del-video).

`ffmpeg` debe estar instalado con soporte para `libass`. El workflow lo instala con `apt-get` en cada ejecución. En Windows puedes instalarlo con `winget install --id Gyan.FFmpeg`.

Si el video falla, el pipeline sigue y solo muestra un `WARN` en el log.

### Ejecución local

1. Crea y activa un entorno virtual, e instala las dependencias:

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

2. Crea un archivo `.env` con las mismas variables:

```env
EMAIL_USER=tu_correo@example.com
EMAIL_PASSWORD=tu_contraseña_o_token
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EMAIL_TO=destinatario@example.com
```

3. Ejecuta el pipeline:

```bash
python src/main.py
```

### Flujo de trabajo para cambios

1. Crea una rama desde `main` (por ejemplo `feature/...`).
2. Sube la rama y lánzala con `workflow_dispatch` para probarla en CI, sin esperar al cron.
3. Revisa el artefacto y el correo.
4. Abre un pull request hacia `main` y fusiónalo cuando la prueba esté bien.

