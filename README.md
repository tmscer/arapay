
# Arapay

Management system for school related payments.

## Installation

It is optimal to install to a virtual environment.

```bash
python3 -m virtualenv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
python3 arapay/manage.py migrate
```

A secrets file from Google console is required. The path to it can be changed in settings.py. Or supply the credentials through environment variables.
