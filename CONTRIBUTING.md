# Contributing to Obelisk

Thank you for considering contributing to Obelisk! This document provides guidelines and instructions for contributing.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/usrbinkat/obelisk.git
   cd obelisk
   ```

2. Install dependencies with Poetry:
   ```bash
   poetry install
   ```

3. Use Task for common operations:
   ```bash
   # List available tasks
   task -l
   
   # Start the development server
   task run
   ```

## Testing

Before submitting a pull request, please test your changes:

```bash
# Run a strict build test
task test
```

## Pull Request Process

1. Fork the repository and create a new branch for your feature
2. Make your changes
3. Test your changes thoroughly
4. Create a pull request with a clear description of the changes
5. Update the README.md with details of changes if needed

## Code Style

- Follow the existing code style
- Use meaningful commit messages
- Add docstrings and comments where appropriate

## License

By contributing to Obelisk, you agree that your contributions will be licensed under the project's MIT License.