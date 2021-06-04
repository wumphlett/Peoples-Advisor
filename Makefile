.PHONY: check, format, req, test

check:
	@poetry run black peoples_advisor --check
	@poetry run pylama

format:
	@poetry run black peoples_advisor

req:
	@poetry export -o peoples_advisor/requirements.txt --without-hashes

test:
	@poetry run pytest
