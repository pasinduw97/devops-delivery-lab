# Verification record

Verified locally on Windows on 5 October 2026.

| Check | Result |
| --- | --- |
| Unit and HTTP integration tests | 18 passed |
| Deterministic Lambda ZIP | Two builds produced the same SHA256 |
| Local smoke test | Health and expected release version passed |
| Wrong release identifier | Smoke test correctly returned a failure |
| Terraform formatting | Passed |
| Terraform configuration validation | Passed with Terraform 1.14.6 and AWS provider 6.67.0 |
| Provider checksums | Lockfile includes linux_amd64 and windows_amd64 |
| Docker local build | Not run locally; Docker is not installed in the preparation environment |
| GitHub-hosted CI | Pending first published workflow run |
| AWS plan, apply and cloud smoke | Not run; no AWS resources deployed |

Lambda ZIP SHA256:

```text
4965737919942750cf0681de82dd85fd941c79740b0c8abf72e23d217b3f7722
```

The local checks validate application behaviour and configuration syntax. They
do not establish AWS permissions, account quotas, runtime integration, operating
cost or production reliability. Add a dated hosted CI link and AWS deployment
evidence when those exercises have actually been completed.
