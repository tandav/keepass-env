.PHONY: bumpver
bumpver:
	# usage: make bumpver PART=minor
	bumpver update --no-fetch --$(PART)
