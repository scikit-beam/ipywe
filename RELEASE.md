# To release a new version of ipywe on conda:

* Update _version.py (set release version, remove 'dev')
* git add and git commit
* And run
```
conda build conda-recipes
anaconda login
anaconda upload /path/to/ipywe-...tar.bz2
git tag -a X.X.X -m 'comment'
```

* Update _version.py (add 'dev' and increment minor)
* And run
```
git add and git commit
git push
git push --tags
```

# To release a new version of ipywe on NPM:
```
# nuke the  `dist` and `node_modules`
git clean -fdx
npm install
npm publish
```
