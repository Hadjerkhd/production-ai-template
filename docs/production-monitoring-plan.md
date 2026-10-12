# Production Monitoring Readiness Plan

## Goal

Make the FastAPI and Vertex AI service observable, operable, and resistant to accidental or abusive spend. This is a staged implementation plan; it does not claim these controls are already implemented.

## Selected Decisions and Implemented Scope

To avoid adding infrastructure, the initial implementation uses these defaults:

- Use Python's standard logging with JSON records, generated request IDs, and request/model durations. Never log prompts, completions, or caller credentials.
- Keep `/api/v1/health` as cheap process liveness and add `/api/v1/ready` for local configuration readiness. Neither endpoint calls Vertex AI.
- Reject empty prompts and prompts longer than 12,000 characters. Cap model output at 512 tokens and the Vertex invocation at 35 seconds, with one provider retry.
- Apply a global in-process quota of 20 generation requests per minute and configure Cloud Run for at most one instance with concurrency four. This deliberately accepts a single-instance capacity limit to avoid Redis/Memorystore.
- Treat the limiter as a coarse global throttle, not a per-caller quota. Its counter resets when the process restarts. A single Cloud Run instance keeps the counter consistent during normal operation but does not make it durable across restarts or deployments.
- Do not claim a hard dollar spend cap. Token limits and request throttling bound exposure but do not estimate or enforce cumulative cost. Durable usage budgets need a shared store, or a verified provider/project quota configured outside the app; both are deferred to avoid introducing an unverified or new dependency.

The implementation covers milestone 1 and the no-resource portions of milestone 2. Dashboards, alert policies, billing budgets, runbooks, and a durable cumulative usage budget remain future work.

## Current Baseline

- Application request and Vertex outcomes are now logged as JSON with severity, request ID, route/model, and duration. Prompt and completion text are not included.
- `/api/v1/health` is a lightweight liveness endpoint; `/api/v1/ready` checks required local model configuration without contacting Vertex AI.
- Prompt length, output tokens, provider invocation time, and generation request rate now have configurable bounds.
- The FastAPI limiter is process-local and global. Cloud Run IAM still provides invocation authentication, not per-caller application quotas or a Vertex spend ceiling.
- The deployment workflow caps Cloud Run at one instance, concurrency four, and a 45-second request timeout. Cloud Run and Vertex AI platform metrics/quotas still need operational dashboards and alerts.
- Docker and Compose already use `/api/v1/health` as a health check. Tests use pytest and can mock the LLM service.

## Recommended Order

### 1. Establish structured application logs and request context

Implement first because logs provide the evidence needed to diagnose failures and tune later limits.

- Configure standard Python logging once at application startup. Emit structured JSON fields that Cloud Logging can parse, including severity, timestamp, service/version, environment, route template, HTTP status, duration, and a generated request ID.
- Use severity consistently: `DEBUG` for local diagnostics only; `INFO` for request completion and normal lifecycle events; `WARNING` for throttling, recoverable provider issues, retries, and degraded dependencies; `ERROR` for failed requests and dependency failures; reserve `CRITICAL` for service-wide inability to operate.
- Add request middleware for request ID and duration. Return the request ID in a response header and include it in error logs so a report can be matched to Cloud Run request logs.
- Keep logs useful but privacy-safe: do not log prompts, model responses, credentials, authorization headers, or raw user identifiers. Prefer route templates and a non-sensitive caller/tenant key where one is available.
- Avoid duplicating Cloud Run's platform request log. Application logs should add request context and business/provider outcomes, not repeat every platform field without value.

**Acceptance checks:** a successful and a failing request produce parseable records at the expected severity; request IDs are present in responses and logs; tests verify that prompt content and credentials are not logged.

### 2. Measure the request and model path

- Record request count, status class, and latency by bounded dimensions such as route, method, and status. Do not label metrics with request IDs, prompt text, or other high-cardinality values.
- Instrument the Vertex call with duration, outcome, retry count, model name, and token usage when the provider returns it. Track input and output token counts separately where available. Do not assume token usage is always returned; expose missing usage as unknown rather than zero.
- Use Cloud Monitoring custom metrics or OpenTelemetry metrics exported to Google Cloud. Keep existing optional MLflow tracing for development/LLM debugging, but do not make production availability depend on MLflow.
- Consider Cloud Trace/OpenTelemetry spans around HTTP handling and the Vertex call. Propagate the request/trace context and ensure trace attributes do not include prompts or sensitive payloads.

**Acceptance checks:** dashboard data distinguishes API latency from model latency, and a test with a mocked provider verifies metrics are emitted on both success and failure.

### 3. Make health and readiness meaningful

- Keep a lightweight liveness endpoint that confirms the process/event loop is responsive and does not call Vertex AI.
- Add a readiness endpoint for startup/configuration checks and required local dependencies. If the service can safely accept requests while Vertex is temporarily unavailable, report process readiness separately from provider health instead of making every provider outage cause restart loops.
- Include a bounded provider availability signal from real request outcomes or a controlled, low-frequency probe only if its latency and cost are understood. Never make every health check invoke Gemini.
- Configure Cloud Run startup/liveness probes (where used) and uptime checks against the appropriate endpoint. Keep Docker/Compose checks aligned with the chosen health semantics.

**Acceptance checks:** liveness remains cheap and succeeds without Vertex credentials; readiness reflects invalid required configuration; health checks do not create model calls.

### 4. Add layered request throttling

- Set request schema bounds, including a maximum prompt length, before provider invocation. Return `413` or `422` for oversized input and `429` for throttling, with a documented retry policy and `Retry-After` where possible.
- Add a FastAPI route-level limiter for `POST /api/v1/generate`. Use a shared backend such as Memorystore/Redis for Cloud Run so limits remain consistent across instances. An in-memory limiter is acceptable only for local development or a deliberately single-process deployment; it is not a production-wide quota.
- Key limits by a verified authenticated caller or tenant. Do not trust a caller-supplied identity header, and do not rely on source IP as the sole identity for service-to-service callers. Confirm how the deployed Cloud Run IAM identity is made available to the application; if it is not available in a trustworthy form, enforce per-consumer quotas at an API gateway or introduce an authenticated identity layer before claiming per-user limits.
- Use separate short-window burst and longer-window quotas. Make thresholds configurable, document per-environment values, and exempt health endpoints from generation quotas.
- Keep Cloud Run maximum instances and concurrency bounded as an additional capacity/cost guard, not as a substitute for caller throttling.

**Acceptance checks:** a caller exceeding the configured quota receives `429`; another caller remains unaffected; limits hold across multiple application instances; limiter-backend failure follows an explicit fail-open/fail-closed policy and is observable.

### 5. Add explicit Vertex AI cost and quota controls

Billing budgets are essential, but **Google Cloud billing budgets and alerts do not stop usage or cap a Vertex AI bill**. Combine provider quotas, application limits, and traffic controls.

- Configure Vertex AI quotas for the selected model/project/region where quota controls are available. Alert on quota consumption and quota errors; verify the exact quota dimensions and adjustable limits in the target project.
- Set a maximum output-token count and input/prompt length for each generation. Keep model and token limits configurable and test the effective request sent to Vertex AI.
- Set bounded provider timeouts and a small, explicit retry policy for transient failures. Do not retry non-retryable errors or rate-limit responses indiscriminately; retries multiply latency and token spend.
- Track token usage and estimate cost using a versioned model-price table or trusted billing data. Record estimated cost and usage at request/model level without storing prompt text. Surface estimation uncertainty and reconcile with Cloud Billing exports.
- Add an application spend/usage budget with a defined enforcement action (for example, reject new expensive calls after a daily tenant/project limit, or temporarily disable generation). Use a durable shared counter and define reset windows; a process-local counter is not suitable on Cloud Run.
- Configure Cloud Run maximum instances, concurrency, and request timeout to bound the rate of concurrent provider calls and runaway scale-out. Treat these as backstops, not exact cost caps.
- Create Cloud Billing budgets and alert thresholds for spend visibility, and document that budget notifications are not a hard cutoff. Review model choice and region against current Vertex pricing and available quotas before launch.

**Acceptance checks:** oversized requests and output limits are rejected/enforced before unbounded spend; a simulated daily budget blocks further generation as designed; configured Vertex quota and Cloud Billing alerts are tested; cost estimates can be reconciled against provider/billing usage.

### 6. Build Cloud Monitoring dashboards and alerts

Create a dashboard for the Cloud Run service and Vertex workload with:

- Request volume, 4xx/5xx rate, p50/p95/p99 latency, instance count, concurrency, and container restarts.
- Vertex call volume, latency, failures, quota errors, retries, input/output tokens, and estimated cost (where available).
- Rate-limit responses and spend/usage budget consumption.

Start with actionable alert policies and route them to an owned notification channel:

- Sustained 5xx/error-rate increase or failed uptime check.
- Elevated p95/p99 latency or Vertex timeout/error rate.
- Vertex quota exhaustion or repeated provider throttling.
- Cloud Run instance/resource saturation or restart loop.
- Application usage budget thresholds and Cloud Billing budget notifications.

Use multi-window or sustained thresholds to reduce alert noise. Every alert should name an owner, include a runbook link, and explain whether the response is customer-impacting, cost-related, or informational.

### 7. Add operational safety and verification

- Add tests for logging severity/context, request IDs, request validation, limiter behavior, budget enforcement, provider timeout/retry handling, and health semantics. Keep all provider calls mocked in unit tests.
- Add an integration test against a fake provider or local stub; do not use billable Vertex calls in normal CI.
- Add a Cloud Run rollout/rollback checklist and runbooks for Vertex quota exhaustion, elevated provider errors, spend alerts, Redis/limiter outage, and unhealthy deployment.
- Define initial service-level objectives, for example availability and p95 latency, only after collecting baseline data. Use error-budget burn alerts rather than arbitrary one-off thresholds once there is enough traffic.
- Review access controls, retention, and redaction for logs/traces. Keep Cloud Run IAM restricted to intended invokers and maintain least privilege for its runtime service account.

## Delivery Milestones

1. **Implemented, tested:** structured logs, request IDs, request/model timing, health/readiness endpoints, and prompt validation.
2. **Partially implemented:** in-process request throttling, output-token/time limits, and Cloud Run scale/concurrency bounds are in place. Durable token/cost accounting, per-caller limits, and a hard cumulative spend budget are deferred because they require shared infrastructure or a verified external quota.
3. **Not started:** Cloud Monitoring dashboards/alerts, Billing budgets, runbooks, and a failure/rollback exercise.
4. **Not started:** OpenTelemetry tracing, measured SLOs, burn-rate alerts, and periodic quota/cost reviews.

## Remaining Operational Decisions

- Before raising Cloud Run above one instance, replace the process-local limiter with a shared limiter or explicitly accept per-instance quotas.
- If cost must be capped rather than bounded, choose a durable usage-budget store or configure a verified Vertex quota with the project owner. Cloud Billing budgets only notify; they do not stop spend.
- Set log/trace retention and alert ownership before enabling production dashboards and notifications.
