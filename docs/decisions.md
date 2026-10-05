# Architecture decisions

## Serverless deployment and local containers

Lambda and API Gateway demonstrate AWS delivery without continuously running
VMs, NAT gateways or managed Kubernetes clusters. The local Docker image exercises
container packaging and runtime hardening. It is a second execution adapter;
the AWS deployment uses a ZIP and does not deploy the Docker image.

## No database or credentials in the service

The API reports health and release identity. It stores no personal information.
The runtime role writes only to its own pre-created log group. There are no AWS
permissions needed for application data access.

## State and deployment identity

Encrypted, versioned S3 state supports recovery and collaboration. S3 lockfiles
avoid a separate DynamoDB lock table. GitHub OIDC removes stored AWS access keys;
the role trust must match one repository and the production environment.

## Explicit operational limits

The public AWS API has no authentication because it exposes only non-sensitive
health and release metadata. The Lambda limit and API throttling reduce load but
cannot enforce a zero-cost guarantee. Logs retain seven days. Alarms need an
existing SNS topic to notify anyone. Deployment has no automated rollback, canary,
multi-region failover, private networking, image registry or Kubernetes cluster.

## Supply chain

There are no pip dependencies. Provider versions are constrained and the generated
Terraform lockfile is committed. Action and base image updates are reviewed via
Dependabot. Actions use verified commit SHAs and the base image uses the official
digest resolved by the hosted build. Pinning controls changes; updates still need
review and verification.
