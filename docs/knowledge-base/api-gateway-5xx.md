# API Gateway 5xx Troubleshooting

Investigate the downstream dependency path before scaling API Gateway.

Checklist:

1. Confirm whether Lambda or container backends are returning 5xx responses.
2. Check recent deployments and configuration drift.
3. Review latency percentiles and database connection saturation.
4. Look for correlated throttling, timeouts, and retry storms.
