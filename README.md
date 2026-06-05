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
