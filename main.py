"""Script to analyze YNAB category spend vs. goals"""

import configparser
import ynab_fetcher
from datetime import date
from operator import attrgetter

CONFIG_FILE = 'config.ini'
HOUSE_CATEGORY_NAME = 'House'
FAILURE_ICON = '\U0000274C'  # Red X
SUCCESS_ICON = '\U00002705'  # Green check mark

class Category:
  def __init__(self, category_json):
    self.name = category_json['name']
    self.budgeted = round(int(category_json['budgeted']) / 1000)
    self.goal = round(int(category_json['goal_target']) / 1000)
    self.spend = round(int(category_json['activity']) / 1000) * -1
    self.over_budget = self.spend > self.goal
    self.goal_type = category_json['goal_type']
  
  def isMonthlySpendingCategory(self):
    return (self.goal != 0 and not self.isSavingCategory() and self.goal_type == 'NEED')

  def isNonMonthlySpendingCategory(self):
    return (self.goal != 0 and not self.isSavingCategory() and self.goal_type != 'NEED')

  def isSavingCategory(self):
    return self.name == HOUSE_CATEGORY_NAME

  def getOutput(self):
    if self.isMonthlySpendingCategory():
      icon = FAILURE_ICON if self.over_budget else SUCCESS_ICON
      spend_diff = abs(self.spend - self.goal)
      over_under_str = 'over' if self.over_budget else 'under'
      return f'{icon} {self.name}: ${spend_diff} {over_under_str} budget (Goal: {self.goal}, Spend: {self.spend})'
    elif self.isNonMonthlySpendingCategory():
      budgeted_over_goal = self.budgeted > self.goal
      icon = FAILURE_ICON if budgeted_over_goal else SUCCESS_ICON
      spend_diff = abs(self.budgeted - self.goal)
      over_under_str = 'over' if budgeted_over_goal else 'under'
      return f'{icon} {self.name}: ${spend_diff} {over_under_str} budget (Goal: {self.goal}, Budgeted: {self.budgeted}, Spend: {self.spend})'
    elif self.isSavingCategory():
      budgeted_to_goal = self.budgeted >= self.goal
      icon = SUCCESS_ICON if budgeted_to_goal else FAILURE_ICON
      save_diff = abs(self.budgeted - self.goal)
      over_under_str = 'over' if budgeted_to_goal else 'under'
      return f'{icon} {self.name}: ${save_diff} {over_under_str} goal (Goal: {self.goal}, Budgeted: {self.budgeted})'

def main():
  config = configparser.ConfigParser()
  config.read(CONFIG_FILE)
  default_config = config['DEFAULT']
  ynab_config = config['api.youneedabudget.com']
  data = ynab_fetcher.GetBudgetMonth(
      ynab_config['ApiKey'], ynab_config['BudgetId'], ynab_config['Month'], default_config.getboolean('CacheBudget'))

  categories = [Category(c) for c in data['data']['month']['categories']]
  savings_categories = [c for c in categories if c.isSavingCategory()]
  monthly_spending_categories = [c for c in categories if c.isMonthlySpendingCategory()]
  non_monthly_spending_categories = [c for c in categories if c.isNonMonthlySpendingCategory()]
  
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

if __name__ == "__main__":
  main()