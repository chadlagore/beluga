import os

# Environment we need to collect.
DATABASE_URL = os.environ.get('DATABASE_URL')

GOOGLE_CLIENT_ID = '148567986475-b6jh9fbl1d0186ku4gibml8619hafbnm.apps.googleusercontent.com'

# This will be used to encrypt short-term cookies
# A random value generated at start should suffice
SECRET_BASE = os.environ.get('SECRET_BASE', os.urandom(64).hex())
