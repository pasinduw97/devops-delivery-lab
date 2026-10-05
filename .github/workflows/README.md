# Delivery workflows

`ci.yml` runs application tests, infrastructure validation and container smoke
checks on pushes to main and pull requests. `deploy.yml` is dispatched manually
from main and uses the protected production environment with AWS OIDC.
