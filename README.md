### ERPNext Update

Update and Cutomize the ERP next

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch version-16
bench install-app erpnext_update
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/erpnext_update
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit

















## Email Account Configuration

The AI email-to-CRM Lead workflow expects an incoming Email Account
named:

Tareqix Mail

Required configuration:

- Email Account Name: Tareqix Mail
- Email Address: info@tareqix.com
- Incoming Email: Enabled
- IMAP: Enabled
- Email Sync Option: UNSEEN
- Initial Sync Count: 250

The mailbox password/OAuth credentials must be configured separately
on the target Frappe site.

Do NOT commit Email Account credentials, OAuth tokens, passwords,
or site_config.json to Git.

## OpenAI Configuration

The application reads the OpenAI API key from the Frappe site
configuration:

openai_api_key

The API key must be configured separately on each site and must
never be committed to Git.
