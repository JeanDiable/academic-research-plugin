# Open-Sourcing academic-research-plugin

Steps to publish this plugin as an open-source Claude Code plugin.

## 1. Create GitHub Repository

```bash
cd /Users/suizhi/Desktop/Research_Claude/academic-research-plugin
git remote add origin git@github.com:suizhi/academic-research-plugin.git
git push -u origin main
```

Replace `suizhi` with your GitHub username if different.

## 2. Add License

Create a `LICENSE` file in the repo root. MIT is recommended for broad adoption:

```bash
# Download MIT license template and fill in your name + year
curl -sL https://opensource.org/licenses/MIT -o LICENSE
```

Or simply create the file manually with MIT text, filling in `2026` and your name.

## 3. Add .gitignore

Create `.gitignore` to exclude generated files:

```
__pycache__/
*.pyc
*.egg-info/
dist/
build/
.env
output/
*.bib
```

## 4. Verify Plugin Structure

Before publishing, validate the plugin:

```bash
claude plugin validate /path/to/academic-research-plugin
```

Ensure the output shows `Validation passed`.

## 5. Push to GitHub

```bash
git add LICENSE .gitignore
git commit -m "chore: add LICENSE and .gitignore for open-source release"
git push origin main
```

## 6. Write GitHub Release

Go to your repo's Releases page and create a `v1.0.0` release:
- Tag: `v1.0.0`
- Title: `v1.0.0 — Initial Release`
- Body: Copy the skill list from README.md

## 7. Enable Others to Install

Users install your plugin with two commands:

```bash
# Add your repo as a marketplace
claude plugin marketplace add suizhi/academic-research-plugin

# Install the plugin
claude plugin install academic-research
```

Document this in the README under "Installation".

## 8. Optional: Submit to Official Marketplace

To get listed in the official Claude plugins directory:

1. Open a PR to [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
2. Add an entry in their `marketplace.json` pointing to your GitHub repo
3. Follow their contribution guidelines for review

## 9. Optional: Add CI

Add a GitHub Actions workflow for basic validation:

```yaml
# .github/workflows/validate.yml
name: Validate Plugin
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r lib/requirements.txt
      - run: python -c "import paper_search; print('OK')" || true
```

## 10. Maintenance

After open-sourcing:
- Pin dependency versions in `requirements.txt` for reproducibility
- Add a CHANGELOG.md for version tracking
- Use semantic versioning: bump version in `plugin.json` on each release
- Run `./sync.sh` after any `lib/` changes before committing

## Checklist

- [ ] GitHub repo created and pushed
- [ ] LICENSE file added (MIT recommended)
- [ ] .gitignore added
- [ ] `claude plugin validate` passes
- [ ] README installation instructions updated with your GitHub URL
- [ ] GitHub release created (v1.0.0)
- [ ] Tested fresh install: `claude plugin marketplace add <repo>` + `claude plugin install academic-research`
