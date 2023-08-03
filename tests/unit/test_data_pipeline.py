from flows.ETL_pipeline import get_year_from_filename

def test_test():
	assert True

def test_get_year_from_filename():
    assert get_year_from_filename('/path/420.csv') == 420
