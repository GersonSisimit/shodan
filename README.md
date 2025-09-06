
# Tarea 4 - Shodan (Script de Consola)

Este repositorio contiene un script de **Python** que usa la **API de Shodan** para realizar una consulta dirigida a **Guatemala** y generar un resumen con:

- **Total de direcciones IP identificadas (únicas).**
- **Total de IPs por puerto abierto.**
- La salida incluye **carnet, nombre, curso y sección**.
- El script **prohíbe** automáticamente el uso del filtro `org:` (por consigna).

---

## 1) Requisitos previos

1. Crear una cuenta en [Shodan](https://account.shodan.io/).
2. Obtener tu **API Key** desde: <https://account.shodan.io/> (Settings → API Key).
3. Tener **Python 3.10+** instalado.

> **Nota:** Shodan aplica límites según tu plan. Si vas a explorar muchas páginas, aumenta `--delay` o reduce `--pages`.

---

## 2) Preparar el entorno

```bash
# Crear entorno (opcional pero recomendado)
python -m venv .venv
# Activar
# Windows:
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install shodan
```

---

## 3) Guardar la API Key (opción A: variable de entorno)

```bash
# Windows (PowerShell)
setx SHODAN_API_KEY "TU_API_KEY_AQUI"

# macOS / Linux (bash/zsh; sólo para la sesión actual)
export SHODAN_API_KEY="TU_API_KEY_AQUI"
```

O bien, **opción B**: pasarla por parámetro `--api-key` al ejecutar.

---

## 4) Ejecutar el script

El script añade **country:GT** a tu consulta automáticamente. **No** permitas `org:` en la query.

**Ejemplo 1 – Buscar por ciudad (Jalapa):**
```bash
python shodan_gt_scan.py --query 'city:"Jalapa"' \

  --carnet 20210000 --nombre "Gerson Sisimit" --curso "Telecomunicaciones II" --seccion "A" \

  --pages 1 --page-size 100
```

**Ejemplo 2 – Buscar RDP en Guatemala:**
```bash
python shodan_gt_scan.py --query 'port:3389' \

  --carnet 20210000 --nombre "Gerson Sisimit" --curso "Telecomunicaciones II" --seccion "A" \

  --pages 1
```

**Ejemplo 3 – Combinar ciudad + puerto:**
```bash
python shodan_gt_scan.py --query 'city:"Chimaltenango" port:80' \

  --carnet 20210000 --nombre "Gerson Sisimit" --curso "Telecomunicaciones II" --seccion "A" \

  --pages 2 --delay 1.2
```

**Parámetros útiles:**
- `--pages` : cuántas páginas traer (por defecto 1).  
- `--page-size` : tamaño de página deseado (Shodan suele devolver hasta 100).  
- `--delay` : pausa entre páginas para evitar límites de rate.  
- `--api-key` : si no usas la variable de entorno `SHODAN_API_KEY`.

---

## 5) ¿Qué imprime?

1. **Encabezado** con tus datos (carnet, nombre, curso, sección).
2. **Todos los resultados** recuperados (de las páginas solicitadas) con:
   - IP, puerto, transporte, ciudad, hostnames y el primer renglón del banner.
3. **Resumen**:
   - Total de resultados listados.
   - Total de IPs únicas identificadas.
   - Tabla “Puerto → IPs únicas”.

---

## 6) Subir a GitHub

1. Crea un repositorio nuevo en tu cuenta (p. ej. `tarea4-shodan-guatemala`).  
2. En la carpeta del proyecto, ejecuta:
   ```bash
   git init
   git add shodan_gt_scan.py README.md
   git commit -m "Tarea 4 - Shodan Guatemala: script y guía"
   git branch -M main
   git remote add origin https://github.com/<tu-usuario>/tarea4-shodan-guatemala.git
   git push -u origin main
   ```
3. Copia la **URL del repositorio** y pégala en tu plataforma de entrega.

---

## 7) Consejos de evaluación
- No uses `org:` en tus queries (el script lo bloquea).
- Incluye tus datos reales en los parámetros para que salgan en la salida.
- Si necesitas más resultados, sube `--pages` gradualmente y usa `--delay` para respetar el rate limit.
- Las consultas de ejemplo del curso (p. ej. `city:"Jalapa"`, puertos comunes) son válidas siempre que apunten a **Guatemala**.
- Cualquier similitud significativa con otro repositorio puede penalizarse (según las reglas de la tarea).

---

## 8) Licencia
Uso académico.
