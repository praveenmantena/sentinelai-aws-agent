# Lambda and Aurora Connection Management

When Lambda concurrency increases sharply, database connection exhaustion can happen before autoscaling reacts.

Recommended actions:

1. Use RDS Proxy between Lambda and Aurora.
2. Limit Lambda concurrency for non-critical functions.
3. Reduce application connection pool sizes.
4. Correlate connection counts with deployment changes and request surges.
