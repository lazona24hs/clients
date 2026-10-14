import os
import re
import requests
from difflib import SequenceMatcher

MAIN_M3U = "marjo.m3u"
ALT_M3U = "buscar.m3u"
TIMEOUT_SECONDS = 5

def clean_name(name):
    """Limpia el nombre del canal para comparaciones flexibles."""
    if not name:
        return ""
    # Pasar a minúsculas, quitar tildes y palabras típicas de calidad/país
    name = name.lower()
    name = re.sub(r'\b(hd|fhd|sd|hq|arg|argentina|oficial|24/7|livestream)\b', '', name)
    # Dejar solo letras y números
    name = re.sub(r'[^a-z0-9]', '', name)
    return name.strip()

def parse_m3u(file_path):
    """Parsea un archivo M3U extrayendo metadatos y URLs."""
    channels = []
    if not os.path.exists(file_path):
        return channels

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    current_meta = ""
    for line in lines:
        line = line.strip()
        if line.startswith("#EXTINF:"):
            current_meta = line
        elif line and not line.startswith("#"):
            url = line
            tvg_id = ""
            tvg_name = ""
            raw_title = ""

            # Extraer tvg-id
            match_id = re.search(r'tvg-id="([^"]+)"', current_meta, re.IGNORECASE)
            if match_id:
                tvg_id = match_id.group(1).lower().strip()

            # Extraer tvg-name o el título después de la coma
            match_name = re.search(r'tvg-name="([^"]+)"', current_meta, re.IGNORECASE)
            if match_name:
                tvg_name = match_name.group(1)
            elif "," in current_meta:
                tvg_name = current_meta.split(",")[-1]

            channels.append({
                "meta": current_meta,
                "url": url,
                "tvg_id": tvg_id,
                "clean_name": clean_name(tvg_name)
            })
            current_meta = ""
    return channels

def is_link_working(url):
    """Comprueba si el enlace responde correctamente y es un manifiesto válido."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)
        if response.status_code == 200:
            if ".m3u8" in url.lower() and "#EXTM3U" in response.text:
                return True
            elif ".m3u8" not in url.lower():
                return True
    except Exception:
        pass
    return False

def find_best_alternative(main_ch, alt_channels):
    """Busca la mejor alternativa por ID exacto, nombre limpio o similitud de texto."""
    # 1. Intentar por tvg-id exacto
    if main_ch["tvg_id"]:
        for alt in alt_channels:
            if alt["tvg_id"] and alt["tvg_id"] == main_ch["tvg_id"]:
                return alt["url"]

    # 2. Intentar por nombre limpio exacto
    if main_ch["clean_name"]:
        for alt in alt_channels:
            if alt["clean_name"] and alt["clean_name"] == main_ch["clean_name"]:
                return alt["url"]

    # 3. Intentar por similitud alta (si no son idénticos pero se parecen mucho)
    if main_ch["clean_name"] and len(main_ch["clean_name"]) > 3:
        best_match_url = None
        highest_ratio = 0.0
        for alt in alt_channels:
            if alt["clean_name"]:
                ratio = SequenceMatcher(None, main_ch["clean_name"], alt["clean_name"]).ratio()
                if ratio > 0.85 and ratio > highest_ratio: # 85% de similitud mínima
                    highest_ratio = ratio
                    best_match_url = alt["url"]
        if best_match_url:
            return best_match_url

    return None

def main():
    main_channels = parse_m3u(MAIN_M3U)
    alt_channels = parse_m3u(ALT_M3U)

    if not main_channels:
        print("La lista principal está vacía o no existe.")
        return

    if not alt_channels:
        print("La lista alternativa está vacía o no existe. No se podrán hacer reemplazos.")
        return

    updated_channels = []
    replaced_count = 0

    for ch in main_channels:
        print(f"Revisando canal...")
        if is_link_working(ch["url"]):
            print("  -> OK (Funciona)")
            updated_channels.append(ch)
        else:
            print("  -> CAÍDO. Buscando coincidencia en alternativas...")
            new_url = find_best_alternative(ch, alt_channels)

            if new_url and is_link_working(new_url):
                print("  -> ¡Encontrado y reemplazado con éxito!")
                ch["url"] = new_url
                replaced_count += 1
            else:
                print("  -> No se encontró alternativa válida o la alternativa también falló. Se mantiene la original.")

            updated_channels.append(ch)

    # Guardar lista principal actualizada
    with open(MAIN_M3U, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in updated_channels:
            f.write(f"{ch['meta']}\n{ch['url']}\n")

    print(f"\nProceso terminado. Total de canales reemplazados: {replaced_count}")

if __name__ == "__main__":
    main()
