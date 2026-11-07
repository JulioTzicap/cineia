let
    // URL pública del backend. No guardar una clave real en Git.
    ApiBaseUrl = "https://cineia-api-nm1g.onrender.com",
    BiApiKey = "REEMPLAZAR_EN_POWER_BI",
    Source = Json.Document(
        Web.Contents(
            ApiBaseUrl,
            [
                RelativePath = "api/v1/bi/consumption",
                Query = [api_key = BiApiKey],
                Timeout = #duration(0, 0, 1, 0)
            ]
        )
    ),
    AsTable = Table.FromRecords(Source),
    Typed = Table.TransformColumnTypes(
        AsTable,
        {
            {"date", type date},
            {"service", type text},
            {"user_email", type text},
            {"requests", Int64.Type},
            {"input_tokens", Int64.Type},
            {"output_tokens", Int64.Type},
            {"total_tokens", Int64.Type}
        }
    )
in
    Typed
