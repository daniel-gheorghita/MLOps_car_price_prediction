test_1:
	echo "makefile works."

test:
	pytest tests/

quality_checks:
	black flows/
	pylint --recursive=y flows/
	
