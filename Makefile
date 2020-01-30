REGISTRY = jthomperoo
NAME = locust-pod-autoscaler
VERSION = latest

default: 
	@echo "=============Building docker image============="
	docker build -t $(REGISTRY)/$(NAME):$(VERSION) .

unittest:
	@echo "=============Running unit tests============="
	coverage run --omit="*/test*" -m pytest
	coverage xml

lint:
	@echo "=============Linting============="
	cd autoscaler && pylint ./* --rcfile=../.pylintrc --ignore-patterns=test_.*?py

doc:
	@echo "=============Serving docs============="
	mkdocs serve