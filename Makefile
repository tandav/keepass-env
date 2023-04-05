.PHONY: test
test:
	pytest --cov keepass_env

.PHONY: bumpver
bumpver:
	# usage: make bumpver PART=minor
	bumpver update --no-fetch --$(PART)
