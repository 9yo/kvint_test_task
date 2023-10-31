import json
import os

import aiofiles
import pytest

from src.report_generator import generate_report
from src.settings import PHONE_DATA_STORAGE_PATH


@pytest.fixture
async def setup_data():
    sample_data = [
        {"phone": 2, "start_date": 0, "end_date": 10, "price": 12},
        {"phone": 2, "start_date": 10, "end_date": 25, "price": 16},
        {"phone": 6, "start_date": 0, "end_date": 15, "price": 18},
        {"phone": 3, "start_date": 0, "end_date": 40, "price": 20}
    ]

    async with aiofiles.open(PHONE_DATA_STORAGE_PATH, 'w') as f:
        await f.write(json.dumps(sample_data))

    yield

    os.remove(PHONE_DATA_STORAGE_PATH)


@pytest.mark.asyncio
async def test_generate_report(setup_data):
    sample_phone_numbers = [2, 6]
    data = await generate_report(sample_phone_numbers)

    # There should be 2 data entries as we queried for 2 numbers
    print(data)
    assert 2 in data and 6 in data

    # Specific checks for phone number 2
    phone_2_data = data[2]
    assert phone_2_data['cnt_all_attempts'] == 2
    assert phone_2_data['min_price_att'] == 12
    assert phone_2_data['max_price_att'] == 16
    assert phone_2_data['cnt_att_dur']['10_sec'] == 1
    assert phone_2_data['cnt_att_dur']['10_30_sec'] == 1

    # Specific checks for phone number 6
    phone_6_data = data[6]
    assert phone_6_data['cnt_all_attempts'] == 1
    assert phone_6_data['min_price_att'] == 18
    assert phone_6_data['max_price_att'] == 18
    assert phone_6_data['cnt_att_dur']['10_30_sec'] == 1
