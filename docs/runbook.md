# Release and incident runbook

## Before a release

Review the commit diff, passing CI, exact release SHA and Terraform plan. Verify
the target account and remote state. Check the alarm topic if notifications are
needed. The default monitoring configuration is not an on-call system.

## Failed post-deployment smoke test

1. Record the failing workflow run and commit SHA. Do not label it an outage
   until the user-facing impact is understood.
2. Query `/healthz` and `/version`. A healthy response with the wrong version
   indicates a release mismatch rather than successful deployment.
3. Inspect API Gateway status/latency logs and Lambda request IDs in CloudWatch.
4. Check `Errors`, `Throttles`, `Duration` and API Gateway 5xx metrics. Inspect
   IAM logging permissions and Lambda concurrency limits when requests fail.
5. Revert the faulty change through a reviewed Git commit, then redeploy from
   main. This lab uses a single Lambda version and has no automatic canary or
   alias rollback. A failed smoke test stops the workflow but does not undo apply.
6. Record cause, impact, recovery and one prevention change in the template below.

## Local fault exercise

Run the local service normally, then run:

```sh
python scripts/smoke.py http://127.0.0.1:8080 --expected-version deliberately-wrong
```

Expect a non-zero result after bounded retries. Run with `--expected-version local`
to show recovery. This simulates release verification failure, not an AWS incident.

## Post-incident template

- Date and environment:
- Observed symptom and affected users:
- Commit and request identifiers:
- Detection mechanism:
- Root cause with supporting logs:
- Recovery steps and verification:
- Prevention change and owner:
- Limits of this exercise:

## Reliability target

After a real AWS exercise, choose a measured target such as a 99% successful
health-check response rate over a specified test window. Record numerator,
denominator, sampling interval and duration. This repository makes no uptime claim.
