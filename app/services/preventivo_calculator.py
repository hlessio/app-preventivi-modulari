from typing import Dict, List
from app.models import PreventivoMasterModel, RigaPreventivo, SezioneTotali, RiepilogoIVA
from decimal import Decimal, ROUND_HALF_UP

# Helper per arrotondamento a 2 cifre decimali
def round_decimal(value: float) -> float:
    return float(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

def calcola_totali_preventivo(preventivo: PreventivoMasterModel) -> None:
    """
    Calcola i subtotali per ogni riga e i totali generali del preventivo.
    Modifica l'oggetto PreventivoMasterModel in-place.
    """
    
    totale_sconti_complessivo = 0.0
    riepilogo_iva_dict: Dict[float, Dict[str, float]] = {}

    # 1. Calcola i totali per ogni riga
    for indice, riga in enumerate(preventivo.corpo_preventivo.righe, start=1):
        # Aggiungi numero di riga
        riga.numero_riga = indice
        
        base_imponibile_riga_pre_sconto = round_decimal(riga.quantita * riga.prezzo_unitario_netto)
        
        importo_sconto_riga = 0.0
        if riga.sconto_riga_percentuale is not None and riga.sconto_riga_percentuale > 0:
            importo_sconto_riga = round_decimal(
                base_imponibile_riga_pre_sconto * (riga.sconto_riga_percentuale / 100.0)
            )
        
        riga.subtotale_riga_netto = round_decimal(base_imponibile_riga_pre_sconto - importo_sconto_riga)
        riga.importo_iva_riga = round_decimal(riga.subtotale_riga_netto * (riga.percentuale_iva / 100.0))
        riga.subtotale_riga_lordo = round_decimal(riga.subtotale_riga_netto + riga.importo_iva_riga)
        
        totale_sconti_complessivo += importo_sconto_riga

        # Aggiorna riepilogo IVA
        aliquota = riga.percentuale_iva
        if aliquota not in riepilogo_iva_dict:
            riepilogo_iva_dict[aliquota] = {"imponibile": 0.0, "iva": 0.0}
        
        riepilogo_iva_dict[aliquota]["imponibile"] += riga.subtotale_riga_netto
        riepilogo_iva_dict[aliquota]["iva"] += riga.importo_iva_riga

    # 2. Calcola i totali generali del preventivo
    totale_imponibile_netto_preventivo = sum(riga.subtotale_riga_netto for riga in preventivo.corpo_preventivo.righe if riga.subtotale_riga_netto is not None)
    totale_iva_preventivo = sum(riga.importo_iva_riga for riga in preventivo.corpo_preventivo.righe if riga.importo_iva_riga is not None)
    
    preventivo.dettagli_totali.totale_imponibile_netto = round_decimal(totale_imponibile_netto_preventivo)
    preventivo.dettagli_totali.totale_sconti = round_decimal(totale_sconti_complessivo) 
    preventivo.dettagli_totali.totale_iva = round_decimal(totale_iva_preventivo)
    preventivo.dettagli_totali.totale_generale_lordo = round_decimal(totale_imponibile_netto_preventivo + totale_iva_preventivo)

    # Compila il riepilogo IVA
    lista_riepilogo_iva: List[RiepilogoIVA] = []
    for aliquota, valori in riepilogo_iva_dict.items():
        lista_riepilogo_iva.append(
            RiepilogoIVA(
                aliquota_percentuale=aliquota,
                imponibile_aliquota=round_decimal(valori["imponibile"]),
                iva_aliquota=round_decimal(valori["iva"])
            )
        )
    preventivo.dettagli_totali.riepilogo_iva = lista_riepilogo_iva 