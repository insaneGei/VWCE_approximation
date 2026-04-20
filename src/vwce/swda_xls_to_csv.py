#!/usr/bin/env python3
"""
Parser: iShares SpreadsheetML (.xls) → CSV

Il file di input è un XML in formato SpreadsheetML (Office XML 2003),
salvato con estensione .xls. Contiene alcune righe di metadati in testa
seguite dalla tabella dati vera e propria, identificata dalla riga
con le celle in stile "headerstyle".

Uso:
    python ishares_xls_to_csv.py input.xls [output.csv]

Se output.csv non è specificato, viene creato nella stessa cartella
dell'input con lo stesso nome e estensione .csv.
"""

import sys
import csv
import re
from pathlib import Path
from xml.etree import ElementTree as ET


# Namespace SpreadsheetML usato da iShares
NS = "urn:schemas-microsoft-com:office:spreadsheet"


def parse_row(row_el) -> list[str]:
    """Estrae i valori testuali da un elemento <ss:Row>."""
    values = []
    for cell in row_el.findall(f"{{{NS}}}Cell"):
        data = cell.find(f"{{{NS}}}Data")
        values.append(data.text if data is not None and data.text else "")
    return values


def is_header_row(row_el) -> bool:
    """
    Restituisce True se TUTTE le celle della riga hanno StyleID='headerstyle'.
    Questa è la riga di intestazione della tabella dati.
    """
    cells = row_el.findall(f"{{{NS}}}Cell")
    if not cells:
        return False
    return all(
        cell.get(f"{{{NS}}}StyleID") == "headerstyle"
        for cell in cells
    )


def strip_bom(path: Path) -> str:
    """Legge il file rimuovendo l'eventuale BOM UTF-8."""
    raw = path.read_bytes()
    # BOM UTF-8: EF BB BF  — anche doppio come in questo file (EFBBBF x2)
    text = raw.decode("utf-8-sig")
    # Rimuove un secondo BOM eventuale (presente nel file originale)
    text = text.lstrip("\ufeff")
    return text


def convert(input_path: Path, output_path: Path) -> int:
    """
    Converte il file SpreadsheetML in CSV.
    Restituisce il numero di righe dati scritte (header escluso).
    """
    xml_text = strip_bom(input_path)

    # ElementTree non accetta la dichiarazione XML con encoding se il
    # testo è già una stringa → la rimuoviamo
    xml_text = re.sub(r"<\?xml[^?]*\?>", "", xml_text, count=1)

    root = ET.fromstring(xml_text)

    # Naviga fino al primo Worksheet → Table
    worksheet = root.find(f"{{{NS}}}Worksheet")
    if worksheet is None:
        raise ValueError("Nessun elemento <ss:Worksheet> trovato nel file.")
    table = worksheet.find(f"{{{NS}}}Table")
    if table is None:
        raise ValueError("Nessun elemento <ss:Table> trovato nel Worksheet.")

    rows = table.findall(f"{{{NS}}}Row")

    # Trova la riga header (headerstyle) e ignora tutto ciò che precede
    header_idx = None
    for i, row in enumerate(rows):
        if is_header_row(row):
            header_idx = i
            break

    if header_idx is None:
        raise ValueError(
            "Impossibile trovare la riga di intestazione (headerstyle). "
            "Verifica che il formato del file non sia cambiato."
        )

    data_rows = rows[header_idx:]  # header + dati

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        records_written = 0
        for row_el in data_rows:
            values = parse_row(row_el)
            # Salta righe completamente vuote
            if not any(v.strip() for v in values):
                continue
            writer.writerow(values)
            records_written += 1

    return records_written - 1  # -1 per escludere la riga header


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"Errore: file non trovato: {input_path}", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        output_path = input_path.with_suffix(".csv")

    print(f"Input : {input_path}")
    print(f"Output: {output_path}")

    try:
        n = convert(input_path, output_path)
        print(f"Conversione completata: {n} righe dati scritte.")
    except Exception as e:
        print(f"Errore durante la conversione: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
