# Documentation Files

Obelisk includes several documentation files to guide developers and users.

## README.md

The primary project README provides an overview of Obelisk:

```markdown
# View README.md contents
cat /workspaces/obelisk/README.md
```

The README typically includes:
- Project description and purpose
- Quick start instructions
- Key features
- Requirements
- Basic usage examples
- Links to more detailed documentation

## CONTRIBUTING.md

Guidelines for contributing to the project:

```markdown
# View CONTRIBUTING.md contents
cat /workspaces/obelisk/CONTRIBUTING.md
```

This file covers:
- How to set up a development environment
- Coding standards and conventions
- Testing requirements
- Pull request process
- Issue reporting guidelines

## CLAUDE.md

Special instructions for Claude AI assistants:

```markdown
# View CLAUDE.md contents
cat /workspaces/obelisk/CLAUDE.md
```

This file provides:
- Project context for Claude AI
- Common commands and workflows
- Code style guidelines
- Specific instructions for AI-assisted development

## LICENSE

The project's license file:

```
# View LICENSE contents
cat /workspaces/obelisk/LICENSE
```

Obelisk is licensed under the MIT License, which:
- Permits commercial use, modification, distribution, and private use
- Requires license and copyright notice inclusion
- Provides no warranty or liability

## Documentation Structure

The documentation content is organized in the `vault` directory, with additional content generated during the build process:

```
vault/
├── assets/                  # Static assets like images
├── cloud/                   # Cloud-related documentation
├── customization/           # Theme customization documentation
├── development/             # Development setup documentation
├── javascripts/             # Custom JavaScript files
├── overrides/               # Theme template overrides
├── stylesheets/             # Custom CSS styles
└── index.md                 # Home page
```

### Generated Documentation

The built documentation is generated to the `site` directory:

```
site/
├── 404.html                 # Not found page
├── assets/                  # Processed assets
├── cloud/                   # Built cloud documentation
├── customization/           # Built customization documentation
├── development/             # Built development documentation
├── index.html               # Built home page
├── search/                  # Search index files
├── sitemap.xml              # Site map for search engines
└── versions.json            # Documentation version information
```