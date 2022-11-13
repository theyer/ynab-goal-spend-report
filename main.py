"""Script to analyze YNAB category spend vs. goals"""

import configparser
import ynab_fetcher
from datetime import date
from enum import Enum
from operator import attrgetter

CONFIG_FILE = 'config.ini'
FAILURE_ICON = '\U0000274C'  # Red X
SUCCESS_ICON = '\U00002705'  # Green check mark
QUESTION_ICON = '\U00002753'  # Red question mark

class CategoryType(Enum):
  UNSPECIFIED = 0
  SAVING = 1
  MONTHLY_SPENDING = 2
  NON_MONTHLY_SPENDING = 3
  NO_GOAL = 4

class Category:
  def __init__(self, category_json, category_config):
    self.config = category_config
    self.name = category_json['name']
    self.hidden = category_json['hidden']
    self.budgeted = round(int(category_json['budgeted']) / 1000)
    self.goal = round(int(category_json['goal_target']) / 1000)
    self.spend = round(int(category_json['activity']) / 1000) * -1
    self.over_budget = self.spend > self.goal
    self.goal_type = category_json['goal_type']

  def type(self):
    if self.name in self.config['SavingCategories']:
      return CategoryType.SAVING
    elif self.goal != 0 and self.goal_type == 'NEED':
      return CategoryType.MONTHLY_SPENDING
    elif self.goal != 0 and self.goal_type != 'NEED':
      return CategoryType.NON_MONTHLY_SPENDING
    elif self.name not in self.config['IgnoredCategories'] and not self.hidden:
      return CategoryType.NO_GOAL
    else:
      return CategoryType.UNSPECIFIED

  def getOutput(self):
    if self.type() == CategoryType.MONTHLY_SPENDING:
      icon = FAILURE_ICON if self.over_budget else SUCCESS_ICON
      spend_diff = abs(self.spend - self.goal)
      over_under_str = 'over' if self.over_budget else 'under'
      return f'{icon} {self.name}: ${spend_diff} {over_under_str} budget (Goal: {self.goal}, Spend: {self.spend})'
    elif self.type() == CategoryType.NON_MONTHLY_SPENDING:
      budgeted_over_goal = self.budgeted > self.goal
      icon = FAILURE_ICON if budgeted_over_goal else SUCCESS_ICON
      spend_diff = abs(self.budgeted - self.goal)
      over_under_str = 'over' if budgeted_over_goal else 'under'
      return f'{icon} {self.name}: ${spend_diff} {over_under_str} budget (Goal: {self.goal}, Budgeted: {self.budgeted}, Spend: {self.spend})'
    elif self.type() == CategoryType.SAVING:
      budgeted_to_goal = self.budgeted >= self.goal
      icon = SUCCESS_ICON if budgeted_to_goal else FAILURE_ICON
      save_diff = abs(self.budgeted - self.goal)
      over_under_str = 'over' if budgeted_to_goal else 'under'
      return f'{icon} {self.name}: ${save_diff} {over_under_str} goal (Goal: {self.goal}, Budgeted: {self.budgeted})'
    elif self.type() == CategoryType.NO_GOAL:
      icon = QUESTION_ICON if self.spend > 0 else SUCCESS_ICON
      return f'{icon} {self.name}: ${self.spend} spent'


def main():
  config = configparser.ConfigParser()
  config.read(CONFIG_FILE)
  default_config = config['DEFAULT']
  category_config = config['CATEGORY']
  ynab_config = config['api.youneedabudget.com']
  data = ynab_fetcher.GetBudgetMonth(
      ynab_config['ApiKey'], ynab_config['BudgetId'], ynab_config['Month'], default_config.getboolean('CacheBudget'))

  categories = [Category(c, category_config) for c in data['data']['month']['categories']]
  savings_categories = [c for c in categories if c.type() == CategoryType.SAVING]
  monthly_spending_categories = [c for c in categories if c.type() == CategoryType.MONTHLY_SPENDING]
  non_monthly_spending_categories = [c for c in categories if c.type() == CategoryType.NON_MONTHLY_SPENDING]
  no_goal_categories = [c for c in categories if c.type() == CategoryType.NO_GOAL]
  
  report_date = date.fromisoformat(ynab_config['Month'])
  report_date_str = report_date.strftime('%B %Y')
  print(f'Report: {report_date_str}')
  print('\n')
  print('------ Savings Report ------')
  [print(o.getOutput()) for o in savings_categories]
  print('\n')
  print('------ Monthly Spending Report ------')
  # Sort on secondary key, then primary key
  monthly_spending_categories.sort(key=attrgetter('name'))
  monthly_spending_categories.sort(key=attrgetter('over_budget'), reverse=True)
  [print(o.getOutput()) for o in monthly_spending_categories]
  print('\n')
  print('------ Non-Monthly Spending Report ------')
  # Sort on secondary key, then primary key
  non_monthly_spending_categories.sort(key=attrgetter('name'))
  non_monthly_spending_categories.sort(key=attrgetter('over_budget'), reverse=True)
  [print(o.getOutput()) for o in non_monthly_spending_categories]
  print('\n')
  print('------ Misc Report ------')
  # Sort on secondary key, then primary key
  no_goal_categories.sort(key=attrgetter('name'))
  no_goal_categories.sort(key=attrgetter('over_budget'), reverse=True)
  [print(o.getOutput()) for o in no_goal_categories]

if __name__ == "__main__":
  main()