# To release a new version of ipywe on conda:

* Update version numbers (set release version, remove 'dev') in 
  - _version.py
  - meta.yaml
  - package.json
* git add and git commit
* tag
```
git tag -a X.X.X -m 'comment'
```
* push
```
git push
git push --tags
```
* And run
```
conda build conda-recipes
anaconda login
anaconda upload /path/to/ipywe-...tar.bz2
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
