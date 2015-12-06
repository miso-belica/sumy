PYTHON=python
VERSION=patch

.PHONY=test publish bump clean


test:
	py.test

publish: test
	${PYTHON} setup.py register sdist bdist_wheel
	twine upload dist/*

bump: test
	bumpversion ${VERSION} --config-file setup.cfg
	git rm .bumpversion.cfg
	git commit --amend

clean:
	rm -rf .bumpversion.cfg .coverage dist build
