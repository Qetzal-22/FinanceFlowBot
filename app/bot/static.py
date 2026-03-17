from aiogram.fsm.state import State, StatesGroup

class CreateBankAccount(StatesGroup):
    name: State