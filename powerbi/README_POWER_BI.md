# Reporte de consumo CineIA en Power BI

## Fuente

1. En Power BI Desktop selecciona **Transformar datos > Nueva fuente > Consulta en blanco**.
2. Abre **Editor avanzado**.
3. Copia el contenido de `CineIA_Consumo.pq`.
4. Sustituye `REEMPLAZAR_EN_POWER_BI` por `BI_API_KEY` y, al publicar, cambia `ApiBaseUrl` por la URL HTTPS de Render.
5. No muestres la clave en capturas ni la subas al repositorio.

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
