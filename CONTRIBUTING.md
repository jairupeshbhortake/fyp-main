# Contributing to DroneVault Analytics

Thank you for considering a contribution! Here is how to get started.

## Development Setup

1. Fork and clone the repository.
2. Follow the **Local development** steps in [README.md](README.md).
3. Create a feature branch: `git checkout -b feat/my-feature`.

## Code Style

**Backend (Python)**
- Formatted with `ruff` — run `ruff check app/` before committing.
- Type hints on all public functions.
- New routes need at least one pytest test in `backend/tests/`.

**Frontend (Vue 3)**
- Use Composition API (`<script setup>`).
- CSS scoped per component. Global tokens in `src/assets/styles/main.css`.
- Run `npm run lint` before committing.

## Submitting a Pull Request

1. Open an issue first for non-trivial changes to align on approach.
2. Keep PRs focused — one feature or fix per PR.
3. Fill in the PR template.
4. All CI checks must pass before review.

## Commit Messages

Follow the Conventional Commits spec:

```
feat: add GPX export for Litchi flights
fix: correct battery health degradation calculation
docs: update deployment guide for PostgreSQL
chore: bump fastapi to 0.112
```

## Reporting Bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).
Include log output and steps to reproduce.

## License

By contributing, you agree your contributions will be licensed under the MIT License.
