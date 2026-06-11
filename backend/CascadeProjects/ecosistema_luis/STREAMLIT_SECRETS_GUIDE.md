# Streamlit Secrets Management Guide

## Overview
This project uses Streamlit's secrets.toml for managing sensitive configuration data like API keys, passwords, and other credentials.

## File Location

### Local/Project-specific secrets
- **Path:** `.streamlit/secrets.toml`
- **Location:** In the working directory (where you call `streamlit run`)
- **Priority:** Takes precedence over global secrets

### Global secrets
- **macOS/Linux:** `~/.streamlit/secrets.toml`
- **Windows:** `%userprofile%/.streamlit/secrets.toml`
- **Purpose:** For secrets shared across multiple projects

## File Format (TOML)

```toml
# Simple key-value pairs
OpenAI_key = "your OpenAI key"
whitelist = ["sally", "bob", "joe"]

# Nested configuration
[database]
user = "your username"
password = "your password"
```

## Usage in Streamlit App

```python
import streamlit as st

# Access simple values
api_key = st.secrets["OpenAI_key"]
is_whitelisted = "sally" in st.secrets.whitelist

# Access nested values
db_user = st.secrets["database"]["user"]
db_password = st.secrets.database.password
```

## Security Best Practices

1. **NEVER commit secrets.toml to version control**
   - Add `.streamlit/secrets.toml` to `.gitignore`
   - Use environment variables in production (Streamlit Cloud, etc.)

2. **Use template files**
   - Create `.streamlit/secrets.toml.template` with placeholder values
   - Commit the template, but not the actual secrets file

3. **Separate development and production secrets**
   - Use local secrets.toml for development
   - Use environment variables or Streamlit Cloud secrets for production

## Template Example

Create `.streamlit/secrets.toml.template`:

```toml
# API Keys
OpenAI_key = "your-openai-key-here"

# Database Configuration
[database]
user = "your-username"
password = "your-password"
host = "localhost"
port = 5432
```

Then copy it to create the actual secrets file:
```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit the actual file with real values
```

## Important Notes for Development

- Always check if secrets are loaded before using them
- Use `.get()` method for optional secrets to avoid errors
- Document required secrets in project README
- Never hardcode credentials in Python files
