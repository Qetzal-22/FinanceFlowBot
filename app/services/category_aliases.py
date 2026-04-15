from app.db import crud
from app.db.models import Category


async def create_category_aliases(user_id: int, category_id: int, key_word: str) -> None:
    await crud.create_category_aliases(user_id, category_id, key_word)

async def get_category_by_key_word_and_user_id(user_id: int, key_word: str) -> Category:
    category_aliases = await crud.get_category_aliases_by_key_word_and_user_id(user_id, key_word)
    if not category_aliases:
        return None
    category = await crud.get_category(category_aliases.category_id)
    return category

