# it-tech-tracker
IT Technology Trends Report

## Ejecutar diariamente desde GitHub Actions

Este proyecto puede ejecutarse todos los días desde GitHub Actions usando el workflow `.github/workflows/daily-report.yml`.

### Configurar secrets en GitHub para el envío de correos

Agrega los siguientes secrets en el repositorio de GitHub:

- `EMAIL_USER`: dirección de correo que enviará el informe.
- `EMAIL_PASS`: contraseña o token de aplicación del correo emisor.
- `SMTP_HOST`: servidor SMTP (por ejemplo `smtp.gmail.com`).
- `SMTP_PORT`: puerto SMTP (por ejemplo `587`).
- `EMAIL_TO`: dirección de correo destinataria.

> Si usas Gmail, lo más probable es que necesites usar un App Password en vez de tu contraseña normal. Gmail suele rechazar el acceso SMTP cuando la cuenta tiene verificación en dos pasos o cuando no se usa un App Password.

Para Gmail, sigue estos pasos:

1. Activa la verificación en dos pasos en tu cuenta de Google.
2. Ve a `https://myaccount.google.com/security`.
3. En "Contraseñas de aplicaciones", crea una contraseña para "Correo" y "Otro (nombre personalizado)".
4. Copia el App Password y pégalo en el secret `EMAIL_PASS`.
5. Asegúrate de que `EMAIL_USER` sea tu correo completo, por ejemplo `tu_correo@gmail.com`.

Opciones típicas para Gmail:

```env
EMAIL_USER=tu_correo@gmail.com
EMAIL_PASS=tu_app_password_generado
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EMAIL_TO=destinatario@example.com
```

### Estrategia práctica que sí puedes usar ya

Con la infraestructura que ya tienes (Python + GitHub Actions + email), puedes resolverlo así:

1. GitHub Actions ejecuta tu script diariamente y manda un correo con el reporte.
2. El correo incluye un bloque “Texto sugerido para LinkedIn”, generado automáticamente.
3. Solo te falta un paso manual: copiar y pegar ese bloque en tu perfil de LinkedIn cada día.

Esto ya funciona con el flujo actual.

### Ejecución local

Para ejecutar localmente, crea un archivo `.env` con las mismas variables:

```env
EMAIL_USER=tu_correo@example.com
EMAIL_PASS=tu_contraseña_o_token
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EMAIL_TO=destinatario@example.com
```

Luego ejecuta:

```bash
python src/main.py
```
