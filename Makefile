PYTHON=python
VERSION=patch

.PHONY=test publish bump clean


test:
	py.test-2.6 && py.test-3.2 && py.test-2.7 && py.test-3.3 && py.test-3.4

publish: test
	${PYTHON} setup.py register sdist bdist_wheel
	twine upload dist/*

bump: test
	bumpversion ${VERSION} --config-file setup.cfg
	git rm .bumpversion.cfg
	git commit --amend

clean:
	rm -rf .bumpversion.cfg .coverage dist build
