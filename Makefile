##################################################################
# General #########################################################
##################################################################
.PHONY: help
# help:
#   Print this help message
help:
	@awk 'BEGIN{H="\033[1;34m";C="\033[1;32m";R="\033[0m"} /^# [[:alpha:]].*#+$$/{h=$$0;gsub(/^# */,"",h);gsub(/ *#+$$/,"",h);printf "%s%s:%s\n",H,h,R;next} /^# /{d=substr($$0,3);next} d&&/^[[:alpha:]][[:alnum:]_-]+:/{c=substr($$1,1,length($$1)-1);printf "  %s%-25s%s %s\n",C,c,R,d;next}{d=""}' $(MAKEFILE_LIST)


##################################################################
# Python #########################################################
##################################################################
.PHONY: fmt
# fmt:
#   Format all python code
fmt:
	uv run ruff format .
	uv run ruff check --select I --fix .
	uv run ruff check . --fix

.PHONY: lint
# lint:
#   Lint all python code
lint:
	uv run mypy --strict --no-incremental .

.PHONY: test
# test:
#   Run all tests
test:
	uv run pytest -v .