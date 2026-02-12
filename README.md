# VP Supply Chain Dashboard (Demo)

This is a **Streamlit** web dashboard prototype based on the "VP Supply Chain Dashboard - User Guide".

## Run locally (Windows)

```bash
cd "%USERPROFILE%\\Documents\\vp-supply-chain-dashboard"
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

## Notes
- Data in this demo is **mock/synthetic** to match the dashboard structure (KPIs, charts, alerts, simulation).
- You can later replace the `data/mock_data.py` generators with real connectors to VMS/TMS/ERP/CRM.
