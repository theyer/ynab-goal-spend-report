from abc import ABC, abstractmethod
from configparser import SectionProxy
from typing import Optional

FAILURE_ICON = '\U0000274C'  # Red X
SUCCESS_ICON = '\U00002705'  # Green check mark
QUESTION_ICON = '\U00002753'  # Red question mark


class Category(ABC):
  def __init__(self, name: str, hidden: bool, budgeted: int, goal: int,
               spend: int, goal_type: str):
    self.name = name
    self.hidden = hidden
    self.budgeted = budgeted
    self.goal = goal
    self.spend = spend
    self.goal_type = goal_type

  @property
  @abstractmethod
  def successful_category(self) -> bool:
    pass

  @abstractmethod
  def getOutput(self) -> str:
    pass

class MonthlySpendingCategory(Category):
  @property
  def successful_category(self) -> bool:
    spend_under_goal = self.spend <= self.goal
    return spend_under_goal

  def getOutput(self) -> str:
    icon = SUCCESS_ICON if self.successful_category else FAILURE_ICON
    spend_diff = abs(self.spend - self.goal)
    over_under_str = 'under' if self.successful_category else 'over'
    return f'{icon} {self.name}: ${spend_diff} {over_under_str} budget (Goal: ${self.goal}, Spend: ${self.spend})'

class NonMonthlySpendingCategory(Category):
  @property
  def successful_category(self) -> bool:
    budgeted_under_goal = self.budgeted <= self.goal
    return budgeted_under_goal

  def getOutput(self) -> str:
    icon = SUCCESS_ICON if self.successful_category else FAILURE_ICON
    spend_diff = abs(self.budgeted - self.goal)
    over_under_str = 'under' if self.successful_category else 'over'
    return f'{icon} {self.name}: ${spend_diff} {over_under_str} budget (Goal: ${self.goal}, Budgeted: ${self.budgeted}, Spend: ${self.spend})'

class SavingCategory(Category):
  @property
  def successful_category(self) -> bool:
    budgeted_to_goal = self.budgeted >= self.goal
    return budgeted_to_goal

  def getOutput(self) -> str:
    icon = SUCCESS_ICON if self.successful_category else FAILURE_ICON
    save_diff = abs(self.budgeted - self.goal)
    over_under_str = 'over' if self.successful_category else 'under'
    return f'{icon} {self.name}: ${save_diff} {over_under_str} goal (Goal: ${self.goal}, Budgeted: ${self.budgeted})'

class NoGoalCategory(Category):
  @property
  def successful_category(self) -> bool:
    no_spend = self.spend <= 0
    return no_spend

  def getOutput(self) -> str:
    icon = SUCCESS_ICON if self.successful_category else QUESTION_ICON
    return f'{icon} {self.name}: ${self.spend} spent'

def CreateCategory(category_json: dict, category_config: SectionProxy) -> Optional[Category]:
  name = category_json['name']
  hidden = category_json['hidden']
  budgeted = round(int(category_json['budgeted']) / 1000)
  goal = round(int(category_json['goal_target']) / 1000)
  spend = round(int(category_json['activity']) / 1000) * -1
  goal_type = category_json['goal_type']

  if name in category_config['SavingCategories']:
    return SavingCategory(name, hidden, budgeted, goal, spend, goal_type)
  elif goal != 0 and goal_type == 'NEED':
    return MonthlySpendingCategory(name, hidden, budgeted, goal, spend, goal_type)
  elif goal != 0 and goal_type != 'NEED':
    return NonMonthlySpendingCategory(name, hidden, budgeted, goal, spend, goal_type)
  elif name not in category_config['IgnoredCategories'] and not hidden:
    return NoGoalCategory(name, hidden, budgeted, goal, spend, goal_type)
  else:
    return None