"""Script to analyze YNAB category spend vs. goals"""

import json
from operator import attrgetter

BUDGET_FILE = './data/budget_092022.json'
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
  
  def isSpendingCategory(self):
    return self.goal != 0 and not self.isSavingCategory()

  def isSavingCategory(self):
    return self.name == HOUSE_CATEGORY_NAME

  def getOutput(self):
    if self.isSpendingCategory():
      icon = FAILURE_ICON if self.over_budget else SUCCESS_ICON
      spend_diff = abs(self.spend - self.goal)
      over_under_str = 'over' if self.over_budget else 'under'
      return f'{icon} {self.name}: ${spend_diff} {over_under_str} budget (Goal: {self.goal}, Spend: {self.spend})'
    elif self.isSavingCategory():
      budgeted_to_goal = self.budgeted >= self.goal
      icon = SUCCESS_ICON if budgeted_to_goal else FAILURE_ICON
      save_diff = abs(self.budgeted - self.goal)
      over_under_str = 'over' if budgeted_to_goal else 'under'
      return f'{icon} {self.name}: ${save_diff} {over_under_str} goal (Goal: {self.goal}, Budgeted: {self.budgeted})'

# TODO: factor in different goal types
# def isMonthlySpendCategory(category):
#   return category['goal_type'] == 'NEED'

def main():
  with open(BUDGET_FILE) as f:
    data = json.load(f)
  
  categories = [Category(c) for c in data['data']['month']['categories']]
  savings_categories = [c for c in categories if c.isSavingCategory()]
  spending_categories = [c for c in categories if c.isSpendingCategory()]
  
  print('Savings Report')
  print('-----------------------------------------------------')
  [print(o.getOutput()) for o in savings_categories]
  print('\n')
  print('Spending Report')
  print('-----------------------------------------------------')
  # Sort on secondary key, then primary key
  spending_categories.sort(key=attrgetter('name'))
  spending_categories.sort(key=attrgetter('over_budget'), reverse=True)
  [print(o.getOutput()) for o in spending_categories]

if __name__ == "__main__":
  main()