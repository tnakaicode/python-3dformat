# git submodule add "url" "name"

git submodule deinit $1
git rm $1
git config -f .gitmodules --remove-section $1
