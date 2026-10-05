# Verification record

Verified locally on Windows on 5 October 2026.

| Check | Result |
| --- | --- |
| Unit, HTTP integration and smoke-check regression tests | 26 passed |
| Deterministic Lambda ZIP | Two builds produced the same SHA256 |
| Local smoke test | Health and expected release version passed |
| Wrong release identifier | Smoke test correctly returned a failure |
| Terraform formatting | Passed |
| Terraform configuration validation | Passed with Terraform 1.14.6 and AWS provider 6.67.0 |
| Provider checksums | Lockfile includes linux_amd64 and windows_amd64 |
| Docker local build | Not run locally; Docker is not installed in the preparation environment |
| GitHub-hosted CI | Startup retry fix awaiting hosted verification |
| AWS plan, apply and cloud smoke | Not run; no AWS resources deployed |

Lambda ZIP SHA256:

```text
4965737919942750cf0681de82dd85fd941c79740b0c8abf72e23d217b3f7722
```

The local checks validate application behaviour and configuration syntax. They
do not establish AWS permissions, account quotas, runtime integration, operating
cost or production reliability. Add AWS deployment evidence when that exercise
has actually been completed.

## Startup failure and regression

The [first hosted run](https://github.com/pasinduw97/devops-delivery-lab/actions/runs/37375929602)
passed the application tests, Terraform checks and Docker build, then failed when
the smoke check received a connection reset during container startup. The retry
handler covered URL errors but missed that socket error.

The smoke check now retries connection resets and HTTP disconnections within its
existing limit. Regression tests cover both startup errors, the retry limit,
unhealthy responses and an incorrect release identifier. A healthy response still
has to report the exact expected commit before the check succeeds.
