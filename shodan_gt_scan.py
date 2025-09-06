#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GT Shodan Fetcher · Consola
---------------------------
- Usa la API de Shodan.
- Añade automáticamente 'country:GT' si no está presente.
- Rechaza consultas que incluyan el filtro prohibido 'org:'.
- Muestra en consola todos los resultados de las páginas consultadas.
- Al final imprime:
    * Total de resultados listados.
    * Número de IPs únicas.
    * Conteo de IPs por puerto abierto.
- Muestra carnet, nombre, curso y sección en el encabezado.

Ejemplo:
  python gt_shodan.py -q 'city:"Jalapa"' -k YOUR_KEY \
    --carnet 20210000 --nombre "Nombre Apellido" \
    --curso "Telecomunicaciones II" --seccion A \
    --pages 1 --page-size 100
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from collections import defaultdict
from typing import Dict, Iterable, List, Set

try:
    import shodan  # pip install shodan
except Exception:
    print("No se pudo importar 'shodan'. Instálalo con: pip install shodan", file=sys.stderr)
    sys.exit(1)


# -------------------------- Utilidades de CLI -------------------------- #

def cli() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Consulta Shodan enfocada a Guatemala (country:GT) con resumen e impresión en consola."
    )
    ap.add_argument("-k", "--api-key", help="API key de Shodan. Si se omite, usa la variable SHODAN_API_KEY.")
    ap.add_argument("-q", "--query", required=True, help="Consulta base de Shodan (ej.: port:3389 o city:\"Jalapa\").")
    ap.add_argument("--pages", type=int, default=1, help="Cantidad de páginas a recuperar. Por defecto: 1.")
    ap.add_argument("--page-size", type=int, default=100, help="Tamaño de página solicitado (hasta ~100).")
    ap.add_argument("--delay", type=float, default=1.0, help="Pausa (seg.) entre páginas para respetar límites.")
    # Datos académicos (obligatorios en salida)
    ap.add_argument("--carnet", required=True, help="Carnet.")
    ap.add_argument("--nombre", required=True, help="Nombre completo.")
    ap.add_argument("--curso", required=True, help="Curso.")
    ap.add_argument("--seccion", required=True, help="Sección.")
    return ap.parse_args()


# -------------------------- Lógica de validación -------------------------- #

ORG_PATTERN = re.compile(r"(^|[\s(])org:", flags=re.IGNORECASE)

def asegurar_sin_org(consulta: str) -> None:
    """Lanza error si la consulta contiene 'org:' como filtro."""
    if ORG_PATTERN.search(consulta or ""):
        raise ValueError("El filtro 'org:' está prohibido por la consigna. Ajusta la consulta.")

def forzar_country_gt(consulta: str) -> str:
    """Incluye country:GT si no está presente."""
    q = (consulta or "").strip()
    return q if re.search(r"\bcountry\s*:\s*gt\b", q, re.IGNORECASE) else f"({q}) country:GT"


# -------------------------- Salida formateada -------------------------- #

def banner_encabezado(carnet: str, nombre: str, curso: str, seccion: str) -> None:
    print("=" * 78)
    print("REPORTE SHODAN · Enfoque Guatemala (country:GT)")
    print()
    print(f"Carnet  : {carnet}")
    print(f"Nombre  : {nombre}")
    print(f"Curso   : {curso}")
    print(f"Sección : {seccion}")
    print("=" * 78)

def render_linea(idx: int, item: dict) -> str:
    ip = item.get("ip_str") or item.get("ip") or "?"
    port = item.get("port", "?")
    proto = item.get("transport", "?")
    loc = item.get("location") or {}
    city = loc.get("city") or item.get("city") or "?"
    hosts = ",".join((item.get("hostnames") or [])[:3])
    # Primera línea del banner, recortada
    banner = (item.get("data") or "").splitlines()[0][:180] if item.get("data") else ""
    mod = item.get("product") or (item.get("_shodan", {}) or {}).get("module") or "?"
    return (f"[{idx}] {ip}:{port}/{proto}  ciudad={city}  hostnames={hosts}  servicio={mod}\n"
            f"      banner: {banner}")

def print_resumen(total_listados: int, ips_unicas: Set[str], mapa_puertos: Dict[int, Set[str]]) -> None:
    print("\n" + "-" * 78)
    print("RESUMEN")
    print(f"Total de resultados listados: {total_listados}")
    print(f"Total de direcciones IP únicas identificadas: {len(ips_unicas)}")
    if mapa_puertos:
        print("\nTotal de IPs por puerto abierto:")
        print("Puerto\tIPs únicas")
        for p in sorted(mapa_puertos):
            print(f"{p}\t{len(mapa_puertos[p])}")
    else:
        print("No se detectaron puertos en los resultados.")
    print("-" * 78)


# -------------------------- Núcleo de consulta -------------------------- #

def obtener_api_key(preferida: str | None) -> str:
    key = "63rBYYEGmglUwyD2G8eoABZuuBk2nAst"

def buscar_paginado(cliente: shodan.Shodan, consulta: str, paginas: int, page_size: int, pausa: float) -> Iterable[List[dict]]:
    """
    Genera listas de 'matches' por página consultada.
    Se usa 'limit' para solicitar el tamaño de página deseado.
    """
    for page_idx in range(1, max(1, paginas) + 1):
        try:
            resp = cliente.search(consulta, page=page_idx, limit=page_size)
        except shodan.APIError as e:
            print(f"ERROR de Shodan en la página {page_idx}: {e}", file=sys.stderr)
            break
        yield resp.get("matches", []) or []
        if page_idx < paginas:
            time.sleep(max(0.0, pausa))


# -------------------------- Programa principal -------------------------- #

def main() -> int:
    args = cli()

    try:
        asegurar_sin_org(args.query)
        consulta_final = forzar_country_gt(args.query)
        api_key = obtener_api_key(args.api_key)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    # Cliente Shodan
    api = shodan.Shodan(api_key)

    # Encabezado y contexto
    banner_encabezado(args.carnet, args.nombre, args.curso, args.seccion)
    print(f"Consulta Shodan: {consulta_final}")
    print(f"Páginas a consultar: {args.pages}  |  Tamaño de página solicitado: {args.page_size}\n")

    # Acumuladores de resumen
    ip_unicas: Set[str] = set()
    port_map: Dict[int, Set[str]] = defaultdict(set)
    total_listados = 0

    # Recorrido por páginas
    for matches in buscar_paginado(api, consulta_final, args.pages, args.page_size, args.delay):
        if not matches and total_listados == 0:
            print("Sin resultados para la consulta.")
            break
        for idx, r in enumerate(matches, start=1 + total_listados):
            print(render_linea(idx, r))
            ip = r.get("ip_str") or r.get("ip")
            port = r.get("port")
            if ip:
                ip_unicas.add(ip)
                if isinstance(port, int):
                    port_map[port].add(ip)
        total_listados += len(matches)

    # Resumen final
    print_resumen(total_listados, ip_unicas, port_map)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
