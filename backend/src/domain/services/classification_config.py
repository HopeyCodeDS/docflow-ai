"""
Config-driven classification profiles for all supported document types.

Each profile contains:
  - keywords: dict mapping language codes to lists of (keyword, weight) tuples
  - filename_hints: list of substrings to check in filenames
  - exclusive_keywords: keywords that strongly identify this type (1.5x boost)
"""
from typing import Dict, Any

CLASSIFICATION_PROFILES: Dict[str, Dict[str, Any]] = {
    "CMR": {
        "keywords": {
            "en": [
                ("CMR", 3.0),
                ("CONSIGNMENT NOTE", 2.5),
                ("TRANSPORT DOCUMENT", 2.0),
                ("INTERNATIONAL CARRIAGE", 1.5),
                ("PLACE OF DELIVERY", 1.0),
                ("CARRIER", 0.8),
                ("SUCCESSIVE CARRIERS", 1.5),
            ],
            "fr": [
                ("LETTRE DE VOITURE", 2.5),
                ("NOTE DE CONSIGNATION", 2.0),
                ("DOCUMENT DE TRANSPORT", 2.0),
                ("TRANSPORTEUR", 0.8),
            ],
            "de": [
                ("FRACHTBRIEF", 2.5),
                ("BEFOERDERUNGSDOKUMENT", 2.0),
                ("TRANSPORTDOKUMENT", 2.0),
                ("SPEDITEUR", 0.8),
            ],
            "es": [
                ("CARTA DE PORTE", 2.5),
                ("DOCUMENTO DE TRANSPORTE", 2.0),
                ("NOTA DE CONSIGNACION", 2.0),
            ],
        },
        "filename_hints": ["CMR", "CONSIGNMENT"],
        "exclusive_keywords": ["CMR"],
    },
    "INVOICE": {
        "keywords": {
            "en": [
                ("INVOICE", 3.0),
                ("TAX INVOICE", 3.0),
                ("INVOICE NUMBER", 2.5),
                ("INVOICE DATE", 2.0),
                ("BILL TO", 2.0),
                ("SUBTOTAL", 1.5),
                ("VAT", 1.0),
                ("TOTAL DUE", 1.5),
                ("PAYMENT TERMS", 1.0),
            ],
            "fr": [
                ("FACTURE", 3.0),
                ("NUMERO DE FACTURE", 2.5),
                ("DATE DE FACTURE", 2.0),
                ("MONTANT TOTAL", 1.5),
                ("TVA", 1.0),
            ],
            "de": [
                ("RECHNUNG", 3.0),
                ("RECHNUNGSNUMMER", 2.5),
                ("RECHNUNGSDATUM", 2.0),
                ("GESAMTBETRAG", 1.5),
                ("MWST", 1.0),
            ],
            "es": [
                ("FACTURA", 3.0),
                ("NUMERO DE FACTURA", 2.5),
                ("FECHA DE FACTURA", 2.0),
                ("IMPORTE TOTAL", 1.5),
                ("IVA", 1.0),
            ],
        },
        "filename_hints": ["INVOICE", "INV", "FACTURE", "RECHNUNG", "FACTURA"],
        "exclusive_keywords": [],
    },
    "DELIVERY_NOTE": {
        "keywords": {
            "en": [
                ("DELIVERY NOTE", 3.0),
                ("DELIVERY RECEIPT", 2.5),
                ("PROOF OF DELIVERY", 2.5),
                ("GOODS RECEIVED", 2.0),
                ("DELIVERED TO", 1.5),
                ("DELIVERY DATE", 1.5),
            ],
            "fr": [
                ("BON DE LIVRAISON", 3.0),
                ("PREUVE DE LIVRAISON", 2.5),
                ("DATE DE LIVRAISON", 1.5),
            ],
            "de": [
                ("LIEFERSCHEIN", 3.0),
                ("LIEFERNACHWEIS", 2.5),
                ("LIEFERDATUM", 1.5),
            ],
            "es": [
                ("ALBARAN", 3.0),
                ("NOTA DE ENTREGA", 3.0),
                ("COMPROBANTE DE ENTREGA", 2.5),
            ],
        },
        "filename_hints": ["DELIVERY", "DEL", "LIEFERSCHEIN"],
        "exclusive_keywords": [],
    },
    "BILL_OF_LADING": {
        "keywords": {
            "en": [
                ("BILL OF LADING", 3.0),
                ("B/L", 2.5),
                ("NOTIFY PARTY", 1.5),
                ("PORT OF LOADING", 2.0),
                ("PORT OF DISCHARGE", 2.0),
                ("VESSEL", 1.5),
                ("VOYAGE", 1.5),
                ("OCEAN BILL", 2.5),
                ("SHIPPED ON BOARD", 2.0),
            ],
            "fr": [
                ("CONNAISSEMENT", 3.0),
                ("PORT DE CHARGEMENT", 2.0),
                ("PORT DE DECHARGEMENT", 2.0),
            ],
            "de": [
                ("KONNOSSEMENT", 3.0),
                ("LADEHAFEN", 2.0),
                ("LOESCHHAFEN", 2.0),
            ],
            "es": [
                ("CONOCIMIENTO DE EMBARQUE", 3.0),
                ("PUERTO DE CARGA", 2.0),
                ("PUERTO DE DESCARGA", 2.0),
            ],
        },
        "filename_hints": ["BOL", "BL", "BILL_OF_LADING", "LADING"],
        "exclusive_keywords": ["BILL OF LADING", "CONNAISSEMENT", "KONNOSSEMENT"],
    },
    "AIR_WAYBILL": {
        "keywords": {
            "en": [
                ("AIR WAYBILL", 3.0),
                ("AWB", 2.5),
                ("AIRWAY BILL", 3.0),
                ("MAWB", 2.5),
                ("HAWB", 2.5),
                ("AIRPORT OF DEPARTURE", 2.0),
                ("AIRPORT OF DESTINATION", 2.0),
                ("IATA", 1.5),
                ("FLIGHT", 1.0),
            ],
            "fr": [
                ("LETTRE DE TRANSPORT AERIEN", 3.0),
                ("LTA", 2.5),
            ],
            "de": [
                ("LUFTFRACHTBRIEF", 3.0),
                ("FLUGHAFEN", 1.0),
            ],
            "es": [
                ("GUIA AEREA", 3.0),
                ("CARTA DE PORTE AEREO", 3.0),
            ],
        },
        "filename_hints": ["AWB", "AIRWAYBILL", "AIR_WAYBILL"],
        "exclusive_keywords": ["AIR WAYBILL", "AWB", "AIRWAY BILL"],
    },
    "SEA_WAYBILL": {
        "keywords": {
            "en": [
                ("SEA WAYBILL", 3.0),
                ("SEAWAY BILL", 3.0),
                ("LINER WAYBILL", 2.5),
                ("NON-NEGOTIABLE", 1.5),
                ("PORT OF LOADING", 1.5),
                ("PORT OF DISCHARGE", 1.5),
            ],
            "fr": [("LETTRE DE TRANSPORT MARITIME", 3.0)],
            "de": [("SEEFRACHTBRIEF", 2.5)],
            "es": [("CARTA DE PORTE MARITIMO", 3.0)],
        },
        "filename_hints": ["SEA_WAYBILL", "SEAWAYBILL", "SWB"],
        "exclusive_keywords": ["SEA WAYBILL", "SEAWAY BILL"],
    },
    "PACKING_LIST": {
        "keywords": {
            "en": [
                ("PACKING LIST", 3.0),
                ("PACKING SLIP", 2.5),
                ("PACKAGE LIST", 2.5),
                ("GROSS WEIGHT", 1.5),
                ("NET WEIGHT", 1.5),
                ("NUMBER OF PACKAGES", 2.0),
                ("DIMENSIONS", 1.0),
                ("MARKS AND NUMBERS", 1.5),
            ],
            "fr": [("LISTE DE COLISAGE", 3.0), ("BORDEREAU", 2.0)],
            "de": [("PACKLISTE", 3.0), ("PACKZETTEL", 2.5)],
            "es": [("LISTA DE EMPAQUE", 3.0), ("LISTA DE EMBALAJE", 3.0)],
        },
        "filename_hints": ["PACKING", "PACK_LIST"],
        "exclusive_keywords": ["PACKING LIST"],
    },
    "CUSTOMS_DECLARATION": {
        "keywords": {
            "en": [
                ("CUSTOMS DECLARATION", 3.0),
                ("CUSTOMS ENTRY", 2.5),
                ("IMPORT DECLARATION", 2.5),
                ("EXPORT DECLARATION", 2.5),
                ("HS CODE", 2.0),
                ("TARIFF CODE", 2.0),
                ("CUSTOMS VALUE", 2.0),
                ("DUTY", 1.5),
                ("COUNTRY OF ORIGIN", 1.5),
            ],
            "fr": [("DECLARATION EN DOUANE", 3.0), ("CODE DOUANIER", 2.0)],
            "de": [("ZOLLANMELDUNG", 3.0), ("ZOLLERKLARUNG", 3.0)],
            "es": [("DECLARACION ADUANERA", 3.0), ("DESPACHO ADUANAL", 2.5)],
        },
        "filename_hints": ["CUSTOMS", "DECLARATION", "ZOLL"],
        "exclusive_keywords": ["CUSTOMS DECLARATION"],
    },
    "CERTIFICATE_OF_ORIGIN": {
        "keywords": {
            "en": [
                ("CERTIFICATE OF ORIGIN", 3.0),
                ("COUNTRY OF ORIGIN", 2.0),
                ("ORIGIN CERTIFICATE", 2.5),
                ("CHAMBER OF COMMERCE", 1.5),
                ("PREFERENTIAL ORIGIN", 2.0),
                ("EUR.1", 2.0),
            ],
            "fr": [("CERTIFICAT D'ORIGINE", 3.0), ("PAYS D'ORIGINE", 2.0)],
            "de": [("URSPRUNGSZEUGNIS", 3.0), ("URSPRUNGSLAND", 2.0)],
            "es": [("CERTIFICADO DE ORIGEN", 3.0), ("PAIS DE ORIGEN", 2.0)],
        },
        "filename_hints": ["ORIGIN", "COO", "CERTIFICATE"],
        "exclusive_keywords": ["CERTIFICATE OF ORIGIN"],
    },
    "DANGEROUS_GOODS_DECLARATION": {
        "keywords": {
            "en": [
                ("DANGEROUS GOODS", 3.0),
                ("HAZARDOUS MATERIALS", 2.5),
                ("DGD", 2.5),
                ("IMDG", 2.0),
                ("UN NUMBER", 2.5),
                ("PROPER SHIPPING NAME", 2.0),
                ("HAZARD CLASS", 2.0),
                ("PACKING GROUP", 1.5),
                ("EMERGENCY CONTACT", 1.0),
            ],
            "fr": [("MARCHANDISES DANGEREUSES", 3.0), ("MATIERES DANGEREUSES", 2.5)],
            "de": [("GEFAHRGUT", 3.0), ("GEFAHRGUTERKLAERUNG", 3.0)],
            "es": [("MERCANCIAS PELIGROSAS", 3.0), ("MATERIALES PELIGROSOS", 2.5)],
        },
        "filename_hints": ["DGD", "DANGEROUS", "HAZARDOUS", "GEFAHRGUT"],
        "exclusive_keywords": ["DANGEROUS GOODS DECLARATION", "DGD"],
    },
    "FREIGHT_BILL": {
        "keywords": {
            "en": [
                ("FREIGHT BILL", 3.0),
                ("FREIGHT INVOICE", 3.0),
                ("FREIGHT CHARGES", 2.5),
                ("SHIPPING CHARGES", 2.0),
                ("FREIGHT RATE", 2.0),
                ("DEMURRAGE", 1.5),
                ("DETENTION", 1.0),
            ],
            "fr": [("FACTURE DE FRET", 3.0), ("FRAIS DE TRANSPORT", 2.0)],
            "de": [("FRACHTRECHNUNG", 3.0), ("FRACHTKOSTEN", 2.0)],
            "es": [("FACTURA DE FLETE", 3.0), ("COSTOS DE FLETE", 2.0)],
        },
        "filename_hints": ["FREIGHT", "FRET", "FRACHT"],
        "exclusive_keywords": [],
    },
}

# Confidence thresholds
CONFIDENT_THRESHOLD = 0.6
UNCERTAIN_THRESHOLD = 0.3

# Fuzzy matching threshold (0.0-1.0 similarity ratio)
FUZZY_MATCH_THRESHOLD = 0.85

# Filename match bonus weight
FILENAME_BONUS = 2.0
