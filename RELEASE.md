# To release a new version of ipywe on conda:

* Update version numbers (set release version, remove 'dev') in 
  - _version.py
  - meta.yaml
  - package.json
* git add and git commit
* And run
```
conda build conda-recipes
anaconda login
anaconda upload /path/to/ipywe-...tar.bz2
git tag -a X.X.X -m 'comment'
```

* Update version numbers (add 'dev' and increment minor)
* And run
```
git add and git commit
git push
git push --tags
```

# To release a new version on PyPI:

    python setup.py sdist upload

# To release a new version of ipywe on NPM:
```
# nuke the  `dist` and `node_modules`
git clean -fdx
npm install
npm publish
```
