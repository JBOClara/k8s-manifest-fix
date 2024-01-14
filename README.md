[![build status](https://github.com/JBOClara/k8s-manifest-fix/actions/workflows/main.yml/badge.svg)](https://github.com/JBOClara/k8s-manifest-fix/actions/workflows/main.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/JBOClara/k8s-manifest-fix/main.svg)](https://results.pre-commit.ci/latest/github/JBOClara/k8s-manifest-fix/main)

k8s-manifest-fix
================


### Using k8s-manifest-fix with pre-commit

Add this to your `.pre-commit-config.yaml`

```yaml
-   repo: https://github.com/JBOClara/k8s-manifest-fix
    rev: v0.1.0  # Use the ref you want to point at
    hooks:
    -   id: k8s-manifest-fix
    # -   id: ...
```

### Hooks available

#### `k8s-manifest-fix`
Check if kubernetes resources are matching a prometheus exposing VPA recommendations.
