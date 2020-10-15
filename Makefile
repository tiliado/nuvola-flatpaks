ARGS ?=

lint:
	yamllint .

format:
	isort nufb
	black nufb

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
	cd ~/dev/k3s && ansible-playbook -i hosts.txt -vD playbooks/tiliado.eu-nginx.yml -l tiliado4 --tags flatpak-repo
