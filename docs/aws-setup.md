# Optional AWS setup

No AWS actions were performed while this lab was prepared. Use a separate sandbox
account. Obtain a spending limit before deployment. CloudWatch alarms, logs, API
requests and Lambda execution can incur charges; throttling and budgets do not
guarantee a hard spending cap.

## Bootstrap prerequisites

1. Install Terraform 1.14.6 or later and AWS CLI from their official sources.
2. Sign in using an authorised short-lived AWS SSO session. Do not commit keys.
3. Create a private S3 state bucket in eu-west-2 with public access blocked,
   default encryption and versioning. Retain state until teardown is verified.
4. For GitHub deployment, create or reuse the GitHub OIDC provider. Create a
   deployment role whose trust is limited to this repository's `production`
   environment and audience `sts.amazonaws.com`.
5. Scope deployment permissions to the named lab resources and state key. It
   needs Lambda, API Gateway v2, CloudWatch logs/alarms, IAM role/policy lifecycle
   for `releaseops-lab-runtime`, and `iam:PassRole` only for that runtime role.
   Review permissions with the account administrator; do not grant AdministratorAccess.
6. Create the GitHub `production` environment, restrict it to main, and configure
   a required reviewer if the plan supports it. Environment approval is a setup
   requirement; declaring `environment: production` alone does not create a gate.
7. Set environment variables `AWS_ROLE_ARN` and `TF_STATE_BUCKET`. Optionally set
   `ALARM_TOPIC_ARN` to an existing SNS topic with a confirmed subscription.
   Without the topic, alarms have no external notification actions.

Example role trust conditions (substitute the exact repository if renamed):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"},
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {"StringEquals": {
      "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
      "token.actions.githubusercontent.com:sub": "repo:pasinduw97/devops-delivery-lab:environment:production"
    }}
  }]
}
```

## Review and deploy locally

From the repository root:

```sh
python -m unittest discover -s tests -v
python scripts/package_lambda.py
terraform -chdir=infra init -backend-config=backend.hcl
terraform -chdir=infra validate
terraform -chdir=infra plan -out=deployment.tfplan
terraform -chdir=infra apply deployment.tfplan
terraform -chdir=infra output -raw api_url
```

Copy `infra/backend.hcl.example` to `infra/backend.hcl` and configure your private
bucket before init. An AWS account's Lambda concurrency quota may prevent a
reserved concurrency value of 2; request quota guidance rather than removing
limits without considering the cost implications.

Alternatively, dispatch `Deploy to AWS` from main after all bootstrap and approval
steps are complete. Review changes locally before dispatching; the workflow
applies its saved plan automatically once the environment gate is approved.

## Destroy the lab

Use the same authorised account, backend and variables. Review a destroy plan:

```sh
terraform -chdir=infra plan -destroy -out=teardown.tfplan
terraform -chdir=infra apply teardown.tfplan
```

Confirm that the Lambda, API, log groups, alarms and runtime IAM role are removed.
Bootstrap resources are managed separately. Keep the state bucket for evidence
until you confirm no resources remain; review retained versions and storage costs.

## Official references

- [GitHub OIDC with AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws)
- [Terraform S3 state and lockfiles](https://developer.hashicorp.com/terraform/language/backend/s3)
- [Terraform AWS provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
