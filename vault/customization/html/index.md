# HTML Template Customization

The Material theme in MkDocs can be customized by overriding specific HTML templates. Obelisk uses this feature to customize key parts of the interface without modifying the theme itself.

## Implementation

Template overrides are enabled by setting the `custom_dir` property in `mkdocs.yml`:

```yaml
theme:
  name: material
  custom_dir: vault/overrides
```

All custom templates are placed in the `vault/overrides` directory.

## Main Template Override

The primary template override is `main.html`, which extends the base template and replaces specific blocks:

```html
{% extends "base.html" %}

{% block announce %}
  <a href="https://github.com/usrbinkat/obelisk">
    <span class="twemoji">{% include ".icons/fontawesome/brands/github.svg" %}</span>
    <strong>Obelisk v0.1.0 </strong>&nbsp;released - Start your Obelisk now
  </a>
{% endblock %}

{% block outdated %}
  You're viewing an outdated version of this documentation.
  <a href="{{ '../' ~ base_url }}">
    <strong>Click here to go to the latest version.</strong>
  </a>
{% endblock %}
```

## Template Blocks

The Material theme provides several blocks that can be overridden:

| Block Name | Description |
|------------|-------------|
| `announce` | Content for the announcement bar at the top of the page |
| `outdated` | Message displayed when viewing an outdated version of the documentation |
| `content` | Main content area of the page |
| `extrahead` | Additional content for the HTML head section |
| `footer` | Footer content |

## Key Customizations

### Announcement Banner

The announcement banner is customized to display the current Obelisk version with a link to the GitHub repository:

```html
{% block announce %}
  <a href="https://github.com/usrbinkat/obelisk">
    <span class="twemoji">{% include ".icons/fontawesome/brands/github.svg" %}</span>
    <strong>Obelisk v0.1.0 </strong>&nbsp;released - Start your Obelisk now
  </a>
{% endblock %}
```

### Outdated Version Message

The message for outdated versions is customized to provide clear navigation to the latest version:

```html
{% block outdated %}
  You're viewing an outdated version of this documentation.
  <a href="{{ '../' ~ base_url }}">
    <strong>Click here to go to the latest version.</strong>
  </a>
{% endblock %}
```

## Adding New Template Overrides

To add a new template override:

1. Identify the template file you want to override from the Material theme
2. Create a file with the same name in the `vault/overrides` directory
3. Either extend the base template and override specific blocks, or provide a complete replacement

For example, to override the footer:

```html
{% extends "base.html" %}

{% block footer %}
  <footer class="md-footer">
    <div class="md-footer-meta md-typeset">
      <div class="md-footer-meta__inner md-grid">
        <div class="md-footer-copyright">
          <div class="md-footer-copyright__highlight">
            Powered by Obelisk {{ config.extra.version.default }}
          </div>
        </div>
      </div>
    </div>
  </footer>
{% endblock %}
```

## Full Template Reference

For more information on template customization, refer to the [Material theme documentation](https://squidfunk.github.io/mkdocs-material/customization/).