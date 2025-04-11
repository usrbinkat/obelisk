# CSS Customization

The Obelisk project includes extensive CSS customizations to enhance the appearance and user experience of the default Material theme.

## Implementation

Custom CSS is applied through the `extra_css` setting in `mkdocs.yml`:

```yaml
extra_css:
  - stylesheets/extra.css
```

The primary CSS file is located at `vault/stylesheets/extra.css`.

## Key Customizations

### Theme Colors

Custom color variables are defined in the `:root` selector:

```css
:root {
  /* Primary theme colors - modern purple-blue gradient */
  --md-primary-fg-color: #5e35b1;
  --md-primary-fg-color--light: #9575cd;
  --md-primary-fg-color--dark: #4527a0;
  
  /* Accent color - complementary orange for highlights */
  --md-accent-fg-color: #ff8a65; 
  --md-accent-fg-color--transparent: rgba(255, 138, 101, 0.1);
}
```

### Dark Mode Support

Dark mode specific styles ensure proper contrast and readability:

```css
/* Dark mode custom variables */
[data-md-color-scheme="slate"] {
  --obelisk-box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3), 0 1px 3px rgba(0, 0, 0, 0.2);
}

[data-md-color-scheme="slate"] .md-content {
  background-color: var(--md-default-bg-color);
}
```

### Announcement Banner

A customized announcement banner provides an eye-catching, yet unobtrusive notice at the top of each page:

```css
/* Announcement bar styling */
.md-banner {
  background-color: #ff8a65; /* Orange background */
  color: #212121; /* Dark text */
  padding: 0; /* Remove padding, we'll control this through height */
  font-size: 0.8rem; /* Slightly larger font size */
  line-height: 1; /* Minimal line height */
  height: 36px; /* Balanced height */
  display: flex;
  align-items: center; /* Vertical centering */
  justify-content: center; /* Horizontal centering */
}
```

### Layout Enhancements

Content areas use subtle shadows and rounded corners for a modern look:

```css
.md-content {
  background-color: white;
  border-radius: var(--obelisk-border-radius);
  box-shadow: var(--obelisk-box-shadow);
  padding: 1.5rem;
  margin-bottom: 2rem;
}
```

### Typography Improvements

Font styles and spacing are optimized for readability:

```css
/* Heading styles */
.md-content h1, 
.md-content h2, 
.md-content h3 {
  font-weight: 500;
  margin-top: 2rem;
}

.md-content h1 {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: var(--md-primary-fg-color--dark);
}
```

### Admonition & Callout Styling

Enhanced styling for admonitions and custom callouts:

```css
/* Special styling for Obsidian compatibility */
.admonition {
  border-radius: var(--obelisk-border-radius);
  margin: 1.5em 0;
  box-shadow: var(--obelisk-box-shadow);
  border: none;
  transition: var(--obelisk-transition);
}

/* Custom callouts */
.callout {
  border-left: 4px solid var(--md-primary-fg-color);
  padding: 1em 1.5em;
  margin: 1.2em 0;
  background-color: var(--md-accent-fg-color--transparent);
  border-radius: 0 var(--obelisk-border-radius) var(--obelisk-border-radius) 0;
  box-shadow: var(--obelisk-box-shadow);
}
```

### Responsive Design

Media queries ensure the design works well on all screen sizes:

```css
/* Mobile Responsiveness Improvements */
@media screen and (max-width: 76.1875em) {
  .md-nav--primary .md-nav__title {
    background-color: var(--md-primary-fg-color);
    color: white;
  }
  
  .md-sidebar--primary {
    background-color: white;
  }
  
  [data-md-color-scheme="slate"] .md-sidebar--primary {
    background-color: var(--md-default-bg-color);
  }
}
```

## Full CSS Reference

For the complete set of CSS customizations, see the [extra.css](../../stylesheets/extra.css) file.