ARGS ?=

lint:
	yamllint .

cdk-experimental: lint
	./nufbctl buildcdk experimental $(ARGS)

adk-experimental: lint
	./nufbctl buildadk experimental $(ARGS)

apps-experimental: lint
	./nufbctl buildbase experimental $(ARGS)
	./nufbctl buildnuvola experimental $(ARGS)
	./nufbctl buildapps experimental $(ARGS)

all-experimental: cdk-experimental adk-experimental apps-experimental
