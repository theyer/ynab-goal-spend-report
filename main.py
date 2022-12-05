"""Script to analyze YNAB category spend vs. goals"""

import category
import configparser
import ynab_fetcher
from datetime import date
from operator import attrgetter

CONFIG_FILE = 'config.ini'


def main():
  config = configparser.ConfigParser()
  config.read(CONFIG_FILE)
  default_config = config['DEFAULT']
  category_config = config['CATEGORY']
  ynab_config = config['api.youneedabudget.com']
  data = ynab_fetcher.GetBudgetMonth(
      ynab_config['ApiKey'], ynab_config['BudgetId'], ynab_config['Month'], default_config.getboolean('CacheBudget'))

  categories = [category.CreateCategory(c, category_config) for c in data['data']['month']['categories']]
  savings_categories = [c for c in categories if isinstance(c, category.SavingCategory)]
  monthly_spending_categories = [c for c in categories if isinstance(c, category.MonthlySpendingCategory)]
  non_monthly_spending_categories = [c for c in categories if isinstance(c, category.NonMonthlySpendingCategory)]
  no_goal_categories = [c for c in categories if isinstance(c, category.NoGoalCategory)]
  
  report_date = date.fromisoformat(ynab_config['Month'])
  report_date_str = report_date.strftime('%B %Y')
  print(f'Report: {report_date_str}')
  note_str = data['data']['month']['note']
  if note_str:
    print('Notes:')
    print(note_str)
  print('\n')
  print('------ Savings Report ------')
  [print(o.getOutput()) for o in savings_categories]
  print('\n')
  print('------ Monthly Spending Report ------')
  # Sort on secondary key, then primary key
  monthly_spending_categories.sort(key=attrgetter('name'))
  monthly_spending_categories.sort(key=attrgetter('successful_category'))
  [print(o.getOutput()) for o in monthly_spending_categories]
  print('\n')
  print('------ Non-Monthly Spending Report ------')
  # Sort on secondary key, then primary key
  non_monthly_spending_categories.sort(key=attrgetter('name'))
  non_monthly_spending_categories.sort(key=attrgetter('successful_category'))
  [print(o.getOutput()) for o in non_monthly_spending_categories]
  print('\n')
  print('------ Misc Report ------')
  # Sort on secondary key, then primary key
  no_goal_categories.sort(key=attrgetter('name'))
  no_goal_categories.sort(key=attrgetter('successful_category'))
  [print(o.getOutput()) for o in no_goal_categories]

if __name__ == "__main__":
  main()