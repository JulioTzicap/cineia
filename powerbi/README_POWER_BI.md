# Reporte de consumo CineIA en Power BI

## Fuente

1. En Power BI Desktop selecciona **Transformar datos > Nueva fuente > Consulta en blanco**.
2. Abre **Editor avanzado**.
3. Para la entrega local, copia el contenido de `CineIA_Consumo.local.pq` (excluido de Git y ya configurado).
4. Para reutilizar la plantilla pública, copia `CineIA_Consumo.pq` y sustituye `REEMPLAZAR_EN_POWER_BI` por `BI_API_KEY`.
5. No muestres la clave en capturas ni la subas al repositorio.

Backend publicado: `https://cineia-api-nm1g.onrender.com`.

## Visualizaciones obligatorias

- Tarjeta: suma de `total_tokens`.
- Tarjeta: suma de `requests`.
- Gráfico de columnas: `service` y suma de `total_tokens`.
- Tabla: fecha, servicio, usuario, solicitudes y tokens.
- Segmentadores: `date` y `service`.

## Medidas DAX

```DAX
Tokens Totales = SUM(CineIA_Consumo[total_tokens])
Solicitudes Totales = SUM(CineIA_Consumo[requests])
Tokens Entrada = SUM(CineIA_Consumo[input_tokens])
Tokens Salida = SUM(CineIA_Consumo[output_tokens])
```

Para la evidencia, aplica el mismo periodo y servicio en la web y Power BI. Los totales deben coincidir porque ambos consumen la misma agregación del backend.
