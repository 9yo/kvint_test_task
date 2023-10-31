import asyncio
from collections import defaultdict
import aiofiles
import ijson
from src.settings import PHONE_DATA_STORAGE_PATH


async def generate_report(phone_numbers: list) -> defaultdict[int, dict]:
    """
    Generate a report for given phone numbers based on their data.

    Parameters:
    - phone_numbers (list): List of phone numbers to generate report for.

    Returns:
    - defaultdict[int, dict]: A dictionary with phone numbers as keys and
                              their stats as values.
    """
    # Initializing the stats with default values
    stats = defaultdict(lambda: {
        'cnt_all_attempts': 0,
        'cnt_att_dur': {
            '10_sec': 0,
            '10_30_sec': 0,
            '30_sec': 0
        },
        'min_price_att': float('inf'),
        'max_price_att': float('-inf'),
        'sum_dur_att': 0,
        'sum_price_att_over_15': 0,
        'num_price_att_over_15': 0
    })

    # Reading the phone data asynchronously
    async with aiofiles.open(PHONE_DATA_STORAGE_PATH, 'rb') as f:
        async for obj in ijson.items(f, 'item'):
            phone = obj['phone']

            # Processing data if phone number matches the given list
            if phone in phone_numbers:
                duration = obj['end_date'] - obj['start_date']

                # Updating stats for the current phone number
                stats[phone]['cnt_all_attempts'] += 1
                stats[phone]['sum_dur_att'] += duration

                # Assume a price field exists in the obj
                price = obj.get('price', 0)
                if price > 15:
                    stats[phone]['sum_price_att_over_15'] += price
                    stats[phone]['num_price_att_over_15'] += 1

                # Update min and max price stats
                stats[phone]['min_price_att'] = min(
                    stats[phone]['min_price_att'], price)
                stats[phone]['max_price_att'] = max(
                    stats[phone]['max_price_att'], price)

                # Categorizing call duration
                if duration <= 10:
                    stats[phone]['cnt_att_dur']['10_sec'] += 1
                elif duration <= 30:
                    stats[phone]['cnt_att_dur']['10_30_sec'] += 1
                else:
                    stats[phone]['cnt_att_dur']['30_sec'] += 1

    # Post-processing the stats
    for phone, phone_stats in stats.items():
        phone_stats['avg_dur_att'] = (
            phone_stats['sum_dur_att'] / phone_stats['cnt_all_attempts']
            if phone_stats['cnt_all_attempts'] else 0
        )
        phone_stats.pop('sum_dur_att', None)
        phone_stats.pop('num_price_att_over_15', None)

    return stats


if __name__ == "__main__":
    sample_phone_numbers = [2, 6]
    report = asyncio.run(generate_report(sample_phone_numbers))
    import pprint
    pprint.pprint(report)
