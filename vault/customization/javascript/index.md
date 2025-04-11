# JavaScript Customization

Obelisk includes custom JavaScript to enhance the user experience beyond what's provided by the standard Material theme.

## Implementation

JavaScript is added through the `extra_javascript` setting in `mkdocs.yml`:

```yaml
extra_javascript:
  - javascripts/extra.js
```

The custom JavaScript file is located at `vault/javascripts/extra.js`.

## Key Features

### Smooth Scrolling

Implements smooth scrolling for anchor links within the same page:

```javascript
// Add smooth scroll behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth'
      });
    }
  });
});
```

### Version Footer

Adds a version indicator to the footer:

```javascript
// Add version text to footer
const footer = document.querySelector('.md-footer-meta');
if (footer) {
  const versionDiv = document.createElement('div');
  versionDiv.className = 'md-footer-version';
  versionDiv.innerHTML = '<span>Obelisk v0.1.0</span>';
  footer.querySelector('.md-footer-meta__inner').appendChild(versionDiv);
}
```

### Cookie Consent Handling

Automatically handles cookie consent in development environments:

```javascript
// Accept cookie consent by default in development
const acceptButtons = document.querySelectorAll('.md-dialog__accept');
if (acceptButtons.length > 0) {
  setTimeout(() => {
    acceptButtons[0].click();
  }, 500);
}
```

## Adding Custom JavaScript

To add new JavaScript functionality:

1. Edit the `extra.js` file or create a new JavaScript file
2. Add the file to the `extra_javascript` list in `mkdocs.yml` if needed
3. Make sure your code is wrapped in a DOM ready event listener:

```javascript
document.addEventListener('DOMContentLoaded', function() {
  // Your code here
});
```

## Integrating with Material Theme

The Material theme provides several JavaScript hooks and events that can be used for customization. Common integration points include:

- **Search functionality** - Customizing search behavior
- **Navigation** - Enhancing navigation interactions
- **Color scheme switching** - Adding custom handling for light/dark mode
- **Content tabs** - Extending tabbed content behavior

## Full JavaScript Reference

For the complete set of JavaScript customizations, see the [extra.js](../../javascripts/extra.js) file.