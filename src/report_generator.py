import asyncio
import json
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


async def read_by_char_range(start_index, end_index) -> str:
    async with aiofiles.open(PHONE_DATA_STORAGE_PATH, 'r') as f:
        await f.seek(start_index)
        return await f.read(end_index - start_index)


async def get_phone_records_by_index(index) -> str:
    RECORDS_PRE_INDEX = 100000

    def calculate_offset(i):
        res = 0
        for numb in range(i):
            res += (64 + (numb // 10)) * RECORDS_PRE_INDEX
        return res

    start = calculate_offset(index) + 1
    end = calculate_offset(index + 1) - 1  # Subtracting 1 to ensure no overlap

    raw_data = await read_by_char_range(start, end)

    # Ensure that the JSON data is well-formed
    last_comma = raw_data.rfind('},')
    if last_comma != -1:
        raw_data = raw_data[:last_comma + 1]

    try:
        return json.loads('[' + raw_data + ']')
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}, while indexing: {index}")
        return []


async def generate_report_fast(phone_numbers: list) -> defaultdict[int, dict]:
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

    for phone_number in phone_numbers:
        phone_number_data = await get_phone_records_by_index(phone_number)
        for obj in phone_number_data:
            duration = obj['end_date'] - obj['start_date']

            # Updating stats for the current phone number
            stats[phone_number]['cnt_all_attempts'] += 1
            stats[phone_number]['sum_dur_att'] += duration

            # Assume a price field exists in the obj
            price = obj.get('price', 0)
            if price > 15:
                stats[phone_number]['sum_price_att_over_15'] += price
                stats[phone_number]['num_price_att_over_15'] += 1

            # Update min and max price stats
            stats[phone_number]['min_price_att'] = min(
                stats[phone_number]['min_price_att'], price)
            stats[phone_number]['max_price_att'] = max(
                stats[phone_number]['max_price_att'], price)

            # Categorizing call duration
            if duration <= 10:
                stats[phone_number]['cnt_att_dur']['10_sec'] += 1
            elif duration <= 30:
                stats[phone_number]['cnt_att_dur']['10_30_sec'] += 1
            else:
                stats[phone_number]['cnt_att_dur']['30_sec'] += 1

    # Post-processing the stats
    for phone, phone_stats in stats.items():
        phone_stats['avg_dur_att'] = (
            phone_stats['sum_dur_att'] / phone_stats['cnt_all_attempts']
            if phone_stats['cnt_all_attempts'] else 0
        )
        phone_stats.pop('sum_dur_att', None)
        phone_stats.pop('num_price_att_over_15', None)

    return stats


# def show_file_structure(first=100):
#     res = defaultdict(int)
#     with open(PHONE_DATA_STORAGE_PATH, 'rb') as f:
#         for obj in ijson.items(f, 'item'):
#             res[obj['phone']] += 1
#     return res
#
#     # defaultdict( <class 'int'>,
#     # {0: 100000,
#     #  ...
#     #  199: 100000})
#
#
# def show_length_of_one_record():
#     with open(PHONE_DATA_STORAGE_PATH, 'rb') as f:
#         for obj in ijson.items(f, 'item'):
#             obj = str(obj)
#             print(obj)  # {'phone': 0, 'start_date': 1684957028364, 'end_date': 1684957074364}
#             return len(obj)  # # 68


#
# def show_length_of_all_phone_records():
#     objects = []
#     with open(PHONE_DATA_STORAGE_PATH, 'rb') as f:
#         for obj in ijson.items(f, 'item'):
#             if obj['phone'] != 0:
#                 return objects
#             objects.append(obj)
#
# def read_by_char_range(start_index, end_index) -> str:
#     with open(PHONE_DATA_STORAGE_PATH, 'r') as f:
#         f.seek(start_index)
#         return f.read(end_index - start_index)
#

# def get_phone_data_by_index(index):
#     read_by_char_range(
#         index * one_phone_block_characters_count,
#         (index + 1) * one_phone_block_characters_count
#     )


if __name__ == "__main__":
    PHONE_DATA_STORAGE_PATH = '/Users/artembogdanov/Downloads/KVINT_TZ/data.json'
    sample_phone_numbers = [n for n in range(20)]
    report = asyncio.run(generate_report_fast(sample_phone_numbers))

    # report = show_file_structure()
    # report = show_length_of_one_record()
    # one_recod_length = show_length_of_one_record() + 1  # add ',' symbol
    # one_recod_length = 64
    # one_phone_block_characters_count = one_recod_length * ONE_PHONE_RECORDS_COUNT

    # one_phone_block_characters_count = show_length_of_all_phone_records() # 6400001
    # data = str(one_phone_block_characters_count).replace(' ', '').replace('\'', '\"')
    # print(data)
    # print(len(data))

    # report = read_by_char_range(1, one_phone_block_characters_count)
    # print(one_recod_length, one_phone_block_characters_count)  # 69 6900000
    #
    # print(report[0:one_recod_length])  # print(report[0:one_recod_length])
    # print(report[-one_recod_length:])
    #
    # report = read_by_char_range(one_phone_block_characters_count + 1, one_phone_block_characters_count * 2)
    #
    # print(report[0:one_recod_length])  # print(report[0:one_recod_length])
    # print(report[-one_recod_length:])
    #
    # report = read_by_char_range(2 * one_phone_block_characters_count + 1, one_phone_block_characters_count * 3)
    #
    # print(report[0:one_recod_length])  # print(report[0:one_recod_length])
    # print(report[-one_recod_length:])
    #
    # report = read_by_char_range(3 * one_phone_block_characters_count + 1, one_phone_block_characters_count * 4)
    #
    # print(report[0:one_recod_length])  # print(report[0:one_recod_length])
    # print(report[-one_recod_length:])

    import pprint

    pprint.pprint(report)
