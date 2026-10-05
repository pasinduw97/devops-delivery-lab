# Explain and extend the lab

Use these questions to review the design, reproduce the checks and identify the
tradeoffs in the delivery workflow.

1. Trace a pull request through CI. Which checks need AWS credentials, and why?
2. Explain the difference between a non-root container and dropping capabilities.
3. Why does the AWS runtime have no S3 permissions even though Terraform uses S3?
4. Explain the OIDC audience and subject conditions. Why use an environment subject?
5. What happens if two workflows apply at once? Explain concurrency and state locking.
6. Why does a saved plan reduce the gap between plan and apply?
7. Show that a healthy endpoint with the wrong release SHA fails verification.
8. Find a request by its ID without logging query strings or request bodies.
9. Describe what this lab's readiness endpoint can and cannot prove.
10. Explain why a budget alert cannot prevent all cloud spending.
11. Describe a reviewed revert and redeploy; explain the absence of automatic rollback.
12. Add a test and small code change yourself. Record the before and after behaviour.

Recommended next extension: a Kubernetes local deployment with resource requests,
limits, liveness/readiness probes and a read-only filesystem. Build it only after
you can demonstrate the current delivery path; avoid adding untested tools solely
for CV keywords.
