CurrencyExchangeEditSchema = {
    "type": "object",
    "properties": {
      "cad_to_usd": {"type": "string"},
      "currency_exchange_id": {"type": "number"},
      "usd_to_cad": {"type": "string"},
    },
    "required": ["cad_to_usd", "currency_exchange_id", "usd_to_cad"]
}
