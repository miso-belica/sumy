PYTHON=python
VERSION=patch

.PHONY=test publish bump clean


test:
	nosetests-2.6 && nosetests-3.2 && nosetests-2.7 && nosetests-3.3

publish: test
	${PYTHON} setup.py register sdist bdist_wheel upload

bump: test
	bumpversion ${VERSION} --config-file setup.cfg
	git rm .bumpversion.cfg
	git commit --amend

clean:
	rm -rf .bumpversion.cfg .coverage dist build
