1. Update patchnotes
2. Update readme
3. Update version in dockerfile
4. Merge to master
5. Tag master with version
  * `git tag -a {version} -m "{version}"`
  * `git tag -a 0.1 -m "0.1"`
6. Push tag
  * `git push --tags`
7. Docker login
8. Build using build script
  * `./build -v {version} .`
  * `./build -v 0.1`
9. Update description on docker hub