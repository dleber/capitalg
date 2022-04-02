from capitalg import utils


def test_convert_timezone():
    DATE_INPUT_FORMAT = "%Y-%m-%dT%H:%M:%S"
    d = utils.convert_timezone(
        '2020-01-01T00:00:00',
        'Australia/Sydney', 
        'America/Los_Angeles'
    )
    assert d.strftime(DATE_INPUT_FORMAT) == '2019-12-31T05:00:00'
    assert str(d.tzinfo) == 'America/Los_Angeles'

    d = utils.convert_timezone(
        '2020-01-01T00:00:00',
        'UTC', 
        'Europe/London'
    )
    assert d.strftime(DATE_INPUT_FORMAT) == '2020-01-01T00:00:00'
    assert str(d.tzinfo) == 'Europe/London'

    # Capture DST
    d = utils.convert_timezone(
        '2020-06-01T00:00:00',
        'UTC', 
        'Europe/London'
    )
    assert d.strftime(DATE_INPUT_FORMAT) == '2020-06-01T01:00:00'
    assert str(d.tzinfo) == 'Europe/London'

    # Same TZ delivers returns same as input 
    d = utils.convert_timezone(
        '2020-06-01T00:00:00',
        'Europe/London', 
        'Europe/London'
    )
    assert d.strftime(DATE_INPUT_FORMAT) == '2020-06-01T00:00:00'
    assert str(d.tzinfo) == 'Europe/London'
    
def test_get_tax_year_cutoff_date():
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
    
    tz = 'Australia/Sydney'
    dt = utils.get_tax_year_cutoff_date('2021-06-30', tz)
    assert dt.strftime(DATE_FORMAT) == '2021-07-01T00:00:00'
    assert str(dt.tzinfo) == tz
    
    tz = 'America/New_York'
    dt = utils.get_tax_year_cutoff_date('2021-12-31', tz)
    assert dt.strftime(DATE_FORMAT) == '2022-01-01T00:00:00'
    assert str(dt.tzinfo) == tz
    