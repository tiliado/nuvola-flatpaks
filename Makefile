ARGS ?=

lint:
	yamllint .

format:
	isort nufb
	black nufb

check: format
	flake8 --format=pylint --show-source nufb
	mypy nufb

cdk-experimental: lint
	./nufbctl buildcdk experimental $(ARGS)

adk-experimental: lint
	./nufbctl buildadk experimental $(ARGS)

apps-experimental: lint
	./nufbctl buildbase experimental $(ARGS)
	./nufbctl buildnuvola experimental $(ARGS)
	./nufbctl buildapps experimental $(ARGS)

all-experimental: cdk-experimental adk-experimental apps-experimental

publish:
	cd ~/dev/k3s && ansible-playbook -i hosts.txt -vD playbooks/tiliado.eu-nginx.yml -l contabo2 --tags flatpak-repo

update-appstream:
	./nufbctl updaterepo
