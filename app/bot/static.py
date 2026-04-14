from aiogram.fsm.state import State, StatesGroup

class CreateBankAccount(StatesGroup):
    name = State()

class CreateTransaction(StatesGroup):
    account_id = State()
    type = State()
    amount = State()
    description = State()
    category = State()

class AddCategory(StatesGroup):
    name = State()

class RenameAccount(StatesGroup):
    name = State()

class CreateBudget(StatesGroup):
    amount = State()

class EditBudget(StatesGroup):
    amount = State()