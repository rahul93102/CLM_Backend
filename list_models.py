#!/usr/bin/env python
"""
List available Gemini models
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')

import django
django.setup()

from django.conf import settings

import google.genai as genai

client = genai.Client(api_key=settings.GEMINI_API_KEY)
# Note: Model listing API may differ in new google.genai
print("Using google.genai for model access")
