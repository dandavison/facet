<img src="./img/facet.png" width="300px"/>

#### Installation
```
$ python3 setup.py develop
$ . completion/bash/facet  # optional tab completion for bash
```

#### Usage
```
Switch contexts.

Usage:
  facet [options] [COMMAND] [ARGS...]
  facet -h|--help

Options:
  -v, --version      Print version and exit

Commands:
  cd                 cd to facet directory
  checkout           cd to facet repo and checkout facet branch
  config             Display facet config
  configure          Configure facet
  create             Create a facet for a JIRA issue
  current            Display current facet
  edit               Edit facet
  fetch              Fetch JIRA data for facet
  follow             Follow/unfollow a facet
  ls                 Display all facets
  migrate            Apply a patch to facet configs
  rm                 Delete facet
  show               Display facet
  workon             Switch to a facet
```
