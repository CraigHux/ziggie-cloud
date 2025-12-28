# GitHub Actions Status Badges

> **Repository**: CraigHux/ziggie-cloud
> **Last Updated**: 2025-12-28

---

## Ready-to-Use Badges

Copy and paste these into your README.md:

### All Badges (Recommended)

```markdown
## CI/CD Status

| Workflow | Status |
|----------|--------|
| Deploy | [![Deploy to Ziggie Cloud](https://github.com/CraigHux/ziggie-cloud/actions/workflows/deploy.yml/badge.svg)](https://github.com/CraigHux/ziggie-cloud/actions/workflows/deploy.yml) |
| Health Check | [![Health Check](https://github.com/CraigHux/ziggie-cloud/actions/workflows/health-check.yml/badge.svg)](https://github.com/CraigHux/ziggie-cloud/actions/workflows/health-check.yml) |
| PR Validation | [![PR Validation](https://github.com/CraigHux/ziggie-cloud/actions/workflows/pr-check.yml/badge.svg)](https://github.com/CraigHux/ziggie-cloud/actions/workflows/pr-check.yml) |
| Rollback | [![Rollback Deployment](https://github.com/CraigHux/ziggie-cloud/actions/workflows/rollback.yml/badge.svg)](https://github.com/CraigHux/ziggie-cloud/actions/workflows/rollback.yml) |
```

### Inline Style

```markdown
[![Deploy](https://github.com/CraigHux/ziggie-cloud/actions/workflows/deploy.yml/badge.svg)](https://github.com/CraigHux/ziggie-cloud/actions/workflows/deploy.yml)
[![Health](https://github.com/CraigHux/ziggie-cloud/actions/workflows/health-check.yml/badge.svg)](https://github.com/CraigHux/ziggie-cloud/actions/workflows/health-check.yml)
[![PR](https://github.com/CraigHux/ziggie-cloud/actions/workflows/pr-check.yml/badge.svg)](https://github.com/CraigHux/ziggie-cloud/actions/workflows/pr-check.yml)
```

---

## Branch-Specific Badges

### Main Branch Only

```markdown
[![Deploy](https://github.com/CraigHux/ziggie-cloud/actions/workflows/deploy.yml/badge.svg?branch=main)](https://github.com/CraigHux/ziggie-cloud/actions/workflows/deploy.yml)
```

### Specific Event

```markdown
<!-- Only show push events -->
[![Deploy](https://github.com/CraigHux/ziggie-cloud/actions/workflows/deploy.yml/badge.svg?event=push)](https://github.com/CraigHux/ziggie-cloud/actions/workflows/deploy.yml)
```

---

## Custom Shields.io Badges

For more customization, use shields.io:

### Dynamic GitHub Actions Badge

```markdown
![Deploy Status](https://img.shields.io/github/actions/workflow/status/CraigHux/ziggie-cloud/deploy.yml?label=Deploy&logo=github)
```

### With Custom Colors

```markdown
![Deploy](https://img.shields.io/github/actions/workflow/status/CraigHux/ziggie-cloud/deploy.yml?style=for-the-badge&label=DEPLOY&logo=github&logoColor=white)
```

### Flat Style

```markdown
![Deploy](https://img.shields.io/github/actions/workflow/status/CraigHux/ziggie-cloud/deploy.yml?style=flat-square&label=deploy)
```

---

## Complete README Badge Section

Add this to the top of your README.md:

```markdown
<div align="center">

# Ziggie Command Center

**AI-Controlled Development Ecosystem**

[![Deploy to Ziggie Cloud](https://github.com/CraigHux/ziggie-cloud/actions/workflows/deploy.yml/badge.svg)](https://github.com/CraigHux/ziggie-cloud/actions/workflows/deploy.yml)
[![Health Check](https://github.com/CraigHux/ziggie-cloud/actions/workflows/health-check.yml/badge.svg)](https://github.com/CraigHux/ziggie-cloud/actions/workflows/health-check.yml)
[![PR Validation](https://github.com/CraigHux/ziggie-cloud/actions/workflows/pr-check.yml/badge.svg)](https://github.com/CraigHux/ziggie-cloud/actions/workflows/pr-check.yml)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg?logo=docker)](https://www.docker.com/)
[![GitHub Stars](https://img.shields.io/github/stars/CraigHux/ziggie-cloud?style=social)](https://github.com/CraigHux/ziggie-cloud)

</div>
```

---

## Additional Useful Badges

### Last Commit

```markdown
![Last Commit](https://img.shields.io/github/last-commit/CraigHux/ziggie-cloud)
```

### Open Issues

```markdown
![Issues](https://img.shields.io/github/issues/CraigHux/ziggie-cloud)
```

### Open Pull Requests

```markdown
![Pull Requests](https://img.shields.io/github/issues-pr/CraigHux/ziggie-cloud)
```

### Code Size

```markdown
![Code Size](https://img.shields.io/github/languages/code-size/CraigHux/ziggie-cloud)
```

### Docker Image Size (if published)

```markdown
![Docker Image Size](https://img.shields.io/docker/image-size/craighux/ziggie-api)
```

---

## Badge Verification

After adding badges, verify they work:

1. Push changes to main branch
2. Wait for workflow to run
3. Check badge shows correct status
4. If badge shows "no status", workflow hasn't run yet

---

## Troubleshooting

### Badge Shows "No Status"

- Workflow hasn't run yet
- Workflow file doesn't exist at that path
- Repository is private (some badges don't work)

### Badge Shows Wrong Status

- Cache issue - add `?t=timestamp` to force refresh
- Wrong branch specified
- Workflow name mismatch

### Badge Not Updating

GitHub caches badges for a few minutes. Add a cache buster:

```markdown
![Status](https://github.com/CraigHux/ziggie-cloud/actions/workflows/deploy.yml/badge.svg?t=20251228)
```

---

**Document Status**: Complete
**Created**: 2025-12-28
