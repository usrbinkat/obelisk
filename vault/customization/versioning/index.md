# Documentation Versioning

Obelisk implements documentation versioning using [Mike](https://github.com/jimporter/mike), which allows maintaining multiple versions of the documentation simultaneously.

## Configuration

Versioning is configured in the `mkdocs.yml` file:

```yaml
extra:
  version:
    provider: mike
    default: 0.1.0
```

## Version Files

The versioning information is stored in two places:

1. **versions.json** - Lists all available versions
2. **Site deployment directories** - Each version has its own directory

The `versions.json` file format:

```json
[
  {
    "version": "0.1.0",
    "title": "0.1.0",
    "aliases": [
      "latest"
    ]
  }
]
```

## Deployment Commands

Version deployment is managed through Taskfile commands:

```yaml
# From Taskfile.yaml
version-deploy:
  desc: "Deploy a new version (requires version number and description)"
  cmds:
    - poetry run mike deploy --push --update-aliases {{.CLI_ARGS}}

version-set-default:
  desc: "Set the default version (requires version number)"
  cmds:
    - poetry run mike set-default --push {{.CLI_ARGS}}
```

Usage:

```bash
# Deploy new version
task version-deploy -- 0.1.0 "Initial boilerplate template release"

# Set as default
task version-set-default -- 0.1.0
```

## Version Selection UI

The Material theme displays a version selection dropdown when versioning is enabled. The styling for this dropdown is customized in `extra.css`:

```css
/* Version selector styling */
.md-version {
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  padding: 0 0.5rem;
}
```

## Outdated Version Notice

When viewing an outdated version, a notice is displayed at the top of the page. This notice is customized in `main.html`:

```html
{% block outdated %}
  You're viewing an outdated version of this documentation.
  <a href="{{ '../' ~ base_url }}">
    <strong>Click here to go to the latest version.</strong>
  </a>
{% endblock %}
```

## Version Integration with Announcement Banner

The current version is displayed in the announcement banner:

```html
{% block announce %}
  <a href="https://github.com/usrbinkat/obelisk">
    <span class="twemoji">{% include ".icons/fontawesome/brands/github.svg" %}</span>
    <strong>Obelisk v0.1.0</strong> released - Start your Obelisk now
  </a>
{% endblock %}
```

## Managing Multiple Versions

To maintain multiple versions:

1. Make changes to the documentation
2. Deploy a new version with an appropriate version number and description
3. Optionally set the new version as the default
4. Users can switch between versions using the dropdown in the UI

## Versioning Best Practices

1. **Semantic Versioning** - Use [SemVer](https://semver.org/) format (MAJOR.MINOR.PATCH)
2. **Clear Descriptions** - Provide meaningful descriptions for each version
3. **Default Version** - Typically set the latest stable version as default
4. **Aliases** - Use aliases like "latest" or "stable" for important versions