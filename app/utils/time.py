from datetime import datetime, date, timedelta


async def create_new_date(old_date: datetime, count_month: int) -> datetime:
    """
    подсчитывает новую дату +/- какое то количество месяцев
    :param old_date:
    :param count_month:
    :return:
    """
    if old_date.month + count_month > 12:
        new_date = datetime(old_date.year + 1, 1, 1)
        new_count_month = count_month - (12 - old_date.month) - 1
        return await create_new_date(new_date, new_count_month)

    elif old_date.month + count_month < 1:
        new_date = datetime(old_date.year - 1, 12, 1)
        new_count_month = count_month - old_date.month
        return await create_new_date(new_date, new_count_month)

    new_date = datetime(old_date.year, old_date.month + count_month, old_date.day)

    return new_date

async def count_day_in_month(d: datetime) -> int:
    next_day = await create_new_date(d, +1)
    count_days = (
            date(next_day.year, next_day.month, next_day.day)
            -
            date(d.year, d.month, d.day)
    ).days

    return count_days