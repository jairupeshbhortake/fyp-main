# User Guide

## Getting Started

1. Open DroneVault in your browser and **register** an account.
2. Log in and land on the **Dashboard**.

---

## Importing Flight Logs

Click **+ IMPORT** in the sidebar. Supported formats:

| Format | Source | Notes |
|--------|--------|-------|
| `.csv` | Litchi app export | Auto-detects metric / imperial units |
| `.txt` | DJI (decoded CSV) | Must be decoded first — see below |

### Preparing DJI Logs

DJI flight logs are binary-encoded. Use one of these tools to decode them to CSV before importing:

- **[CsvView](https://www.phantompilots.com/attachments/csvview-zip.99589/)** — Windows desktop tool
- **[AirData](https://airdata.com)** — web-based, free tier available
- **[dji-log-parser CLI](https://github.com/lvauvillier/dji-log-parser)** — command-line

Save the decoded file as `.txt` and import it into DroneVault.

### Preparing Litchi Logs

In the Litchi app, go to **My Flights** → select flights → **Export CSV**.

---

## Dashboard

The dashboard shows:

- **Stats cards** — aggregate totals for all filtered missions
- **Filters panel** — filter by drone model, source, date range, or minimum duration
- **Mission list** — click any row to load that flight
- **Flight map** — GPS path with HUD overlay
- **Telemetry charts** — altitude, speed, battery %, RC signal
- **Replay button** — animated path playback at 8× speed
- **Export buttons** — CSV and GPX download

---

## Flight Detail

Click the **mission ID** link or navigate to `/flight/:id` for the full detail view:

- All telemetry charts
- Compass / heading indicator
- Battery end-charge and serial
- Anomaly events (rule-based alerts)
- Mission notes (auto-saved on blur)
- Delete flight

---

## Analytics

The **Analytics** page shows:

- Monthly flight activity bar chart
- Flights by drone model
- Distance and altitude distributions

---

## Battery Health

The **Battery** page groups flights by battery serial number and shows:

- Health ring (estimated % capacity remaining)
- Cycle count
- Average end-of-flight charge %
- Status badge (OPTIMAL / FAIR / REPLACE)

---

## Tags

Tags are automatically applied on import:

| Tag | Condition |
|-----|-----------|
| NIGHT | Take-off hour < 06:00 or ≥ 20:00 |
| HI-SPD | Max speed > 15 m/s |
| LOW BATT | Battery end < 20 % |
| HIGH ALT | Max altitude > 120 m |
| LITCHI | Imported from Litchi CSV |
