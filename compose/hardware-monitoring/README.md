# hardware monitoring using prometheus and grafana
## Quick Start
1. spin up containers:
```bash
docker compose up -d
```
2. login to grafana at http://localhost:3002 with default user & password: `admin` & `admin` (you'll be prompted to change the password after the first login)
3. connect the prometheus service as data source:
    1. On the left sidebar navigate to: Connection > Data sources
    2. Add new > select Prometheus
    3. change the Prometheus server URL to `http://prometheus:9090` and hit Save & test
4. Navigate to Dashboards
    1. Add new Dashboard and select Import
    2. Choose the `grafana_dashboard.json` and select the Prometheus data source you just created.
    3. Hit Import
