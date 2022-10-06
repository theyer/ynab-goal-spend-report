"""Module to query YNAB API for budget data."""

import json
import requests
from os import path

BUDGET_MONTH_FILE_TMPL = 'budget_{budget_id}_month_{month}.json'
BUDGET_MONTH_URL_TMPL = 'https://api.youneedabudget.com/v1/budgets/{budget_id}/months/{month}'
CACHE_DIR = 'data'

def GetBudgetMonth(api_key, budget_id, month, cache_budget):
  cache_file_path = path.join(
      CACHE_DIR, BUDGET_MONTH_FILE_TMPL.format(budget_id=budget_id, month=month))
  if cache_budget and path.exists(cache_file_path):
    with open(cache_file_path) as f:
      return json.load(f)

  url = BUDGET_MONTH_URL_TMPL.format(budget_id=budget_id, month=month)
  headers = {'Authorization': f'Bearer {api_key}'}
  data = requests.get(url, headers=headers).json()
  if cache_budget:
    with open(cache_file_path, 'x') as f:
      f.write(json.dumps(data))
  return data