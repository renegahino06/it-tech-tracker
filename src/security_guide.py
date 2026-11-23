MAX_LINES = 8
MAX_LINE_LENGTH = 58
MAX_STEPS = 4

# Comandos de verificación (solo lectura). Cada entrada aplica
# cuando alguna palabra clave aparece en el título de la noticia.
TECH_GUIDES = [
    {
        "name": "OpenSSL",
        "keywords": ["openssl"],
        "description": "Verifica la versión de OpenSSL instalada.",
        "lang": "bash",
        "lines": [
            "openssl version -a",
            "dpkg -l | grep libssl",
            "# Compara con la versión corregida del aviso",
        ],
    },
    {
        "name": "Log4j",
        "keywords": ["log4j", "log4shell"],
        "description": "Busca copias de Log4j vulnerables en el equipo.",
        "lang": "bash",
        "lines": [
            "find / -name 'log4j-core*.jar' 2>/dev/null",
            "unzip -p app.jar META-INF/MANIFEST.MF | grep Version",
            "# Actualiza a la versión corregida del aviso",
        ],
    },
    {
        "name": "OpenSSH",
        "keywords": ["openssh", "ssh"],
        "description": "Revisa la versión de OpenSSH y su configuración.",
        "lang": "bash",
        "lines": [
            "ssh -V",
            "sudo sshd -T | grep -E 'permitrootlogin|passwordauth'",
            "sudo systemctl status ssh",
        ],
    },
    {
        "name": "nginx",
        "keywords": ["nginx"],
        "description": "Confirma la versión de nginx en uso.",
        "lang": "bash",
        "lines": [
            "nginx -v",
            "sudo nginx -T | head -n 20",
            "sudo systemctl status nginx",
        ],
    },
    {
        "name": "Docker",
        "keywords": ["docker"],
        "description": "Revisa la versión de Docker y los contenedores.",
        "lang": "bash",
        "lines": [
            "docker version --format '{{.Server.Version}}'",
            "docker ps --format 'table {{.Names}}\\t{{.Image}}'",
        ],
    },
    {
        "name": "Kubernetes",
        "keywords": ["kubernetes", "kubectl"],
        "description": "Revisa la versión del clúster y de kubectl.",
        "lang": "bash",
        "lines": [
            "kubectl version",
            "kubectl get nodes -o wide",
        ],
    },
    {
        "name": "Node.js",
        "keywords": ["npm", "node.js", "nodejs"],
        "description": "Audita dependencias de Node.js en tu proyecto.",
        "lang": "bash",
        "lines": [
            "npm audit --omit=dev",
            "npm outdated",
        ],
    },
    {
        "name": "Python",
        "keywords": ["python", "pip"],
        "description": "Audita dependencias de Python en tu proyecto.",
        "lang": "bash",
        "lines": [
            "pip install pip-audit",
            "pip-audit -r requirements.txt",
        ],
    },
    {
        "name": "Windows",
        "keywords": ["windows", "microsoft"],
        "description": "Revisa parches instalados en Windows.",
        "lang": "powershell",
        "lines": [
            "Get-HotFix | Sort-Object InstalledOn -Descending | Select -First 5",
            "winver",
        ],
    },
]

# Pasos genéricos de mitigación para noticias de ciberseguridad.
SECURITY_STEPS = [
    "Confirma si tu versión está afectada.",
    "Inventaria los sistemas con ese componente.",
    "Aplica el parche; limita la exposición.",
    "Verifica la versión y revisa los logs.",
]


def _normalize(text):
    text = text.lower()
    for separator in ("-", "_", "/", ",", ":", "(", ")", "'", '"'):
        text = text.replace(separator, " ")
    return f" {' '.join(text.split())} "


def _matches(keyword, title):
    # Coincidencia por palabra completa para que "ssh" no
    # coincida dentro de otra palabra.
    return f" {' '.join(keyword.lower().split())} " in _normalize(title)


def _valid_lines(lines):
    return [
        line
        for line in lines[:MAX_LINES]
        if len(line) <= MAX_LINE_LENGTH
    ]


def _diagram(component, categories):
    # Diagrama defensivo del escenario de riesgo: cómo llega el
    # ataque y en qué puntos se puede frenar.
    if "SECURITY" not in categories:
        return None

    return {
        "nodes": [
            "Internet o red no confiable",
            f"{component or 'Software afectado'} expuesto",
            "Versión sin parche",
            "Acceso no autorizado",
        ],
        "controls": [
            "Limita la exposición",
            "Aplica el parche",
            "Detecta y responde",
        ],
    }


def build_guide(content):
    title = content.get("title", "")
    categories = content.get("categories", [])

    steps = []
    if "SECURITY" in categories:
        steps = SECURITY_STEPS[:MAX_STEPS]

    for guide in TECH_GUIDES:
        if any(_matches(k, title) for k in guide["keywords"]):
            lines = _valid_lines(guide["lines"])
            if lines:
                return {
                    "description": guide["description"],
                    "lang": guide["lang"],
                    "lines": lines,
                    "steps": steps,
                    "specific": True,
                    "diagram": _diagram(guide["name"], categories),
                }

    return {
        "description": "",
        "lang": "",
        "lines": [],
        "steps": steps,
        "specific": False,
        "diagram": _diagram(None, categories),
    }
