# Screenshots

Place your application screenshots in this folder before submission.

## Screenshots to Capture

| Filename | Description |
|---|---|
| `01-home-dashboard.png` | Main dashboard with KPI cards (Total Shipments, At-Risk, Critical, Active Disruptions, Available Vehicles, Fleet Utilisation, Cold-Chain Alerts) and the top at-risk shipments table |
| `02-shipment-analysis.png` | Shipment detail view with risk score breakdown, active disruptions, route alternatives, vehicle recommendation, and the AI Explanation button |
| `03-fleet-cold-chain.png` | Fleet utilisation view showing per-vehicle load percentage table, and the Cold Chain page with temperature excursion alerts and the temperature history line chart |

## How to Take Screenshots

1. Run `streamlit run src/app.py`
2. Navigate to each page and select representative data
3. For `01-home-dashboard.png`: screenshot the Dashboard page with all KPI metrics visible
4. For `02-shipment-analysis.png`: select a CRITICAL or HIGH risk shipment on the Shipments page to show the full detail panel
5. For `03-fleet-cold-chain.png`: screenshot the Fleet page with the vehicle table visible, or the Cold Chain page showing an excursion alert and chart

## Requirements

- Minimum: 3 screenshots
- Format: PNG or JPG
- Show the application running with real mock data (the JSON data files are pre-populated)
- Avoid screenshots of empty or error states
