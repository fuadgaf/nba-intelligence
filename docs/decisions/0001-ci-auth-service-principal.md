# 0001: CI/CD authenticates to Databricks with a service principal and an `all-apis` OAuth secret

**Date:** 2026-11-14
**Status:** Accepted

## Context

GitHub Actions needs to run `databricks bundle validate` on every PR and `databricks bundle deploy -t prod` on merge to `main`. To do that, it has to log in to the workspace without a person present.

## Options

1. **A personal access token.** It's tied to me, long-lived, and has all my rights. Rejected.
2. **A service principal with an OAuth secret limited to specific scopes** (`jobs`, `pipelines` and so on). Tried first, but it failed: the Databricks CLI always asks for an `all-apis` token, and Databricks refuses that for a secret without the `all-apis` scope. I found this by calling the token endpoint directly: `scope=jobs` worked and `scope=all-apis` returned `access_denied`. I found no setting that makes the CLI ask for narrower scopes.
3. **A service principal with an `all-apis` OAuth secret.** Chosen.
4. **GitHub OIDC (workload identity federation).** No stored secret at all, which makes it the best option. Not possible here, because it needs account-level setup and Free Edition has no account console.

## Decision

CI uses the service principal `nba-ci` with an `all-apis` OAuth secret, stored as the GitHub repository secrets `DATABRICKS_CLIENT_ID` and `DATABRICKS_CLIENT_SECRET`.

## Why it's still locked down

The scope says which APIs the token may call. What `nba-ci` can actually do is limited elsewhere:

- **Workspace entitlements:** workspace access only. No admin, no SQL access.
- **Unity Catalog:** privileges on `nba_prod` only.
- **GitHub:** prod deploys run only from `main`, through the `production` environment.

## Consequences

- **The secret expires after 730 days (the maximum)** and Databricks doesn't warn before it does, so rotate it before then: generate a new secret, update GitHub, then delete the old one.
- **If this project moved to a paid workspace,** switch to GitHub OIDC and remove the secret.
