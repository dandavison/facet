#!/bin/bash -eu

export FACET_DIR=~/.facets

facet-cd () {
    cd $FACET_DIR
}

facet-ls () {
    ls $FACET_DIR
}

facet-create () {
    local project=$1
    -facet-assert-not-valid-project $project || return 1
    mkdir $FACET_DIR/$project
    echo "\
name: $project
jira: $project
class: counsyl.website.WebsiteProject" > $FACET_DIR/$project/facet.yaml
}

facet-edit () {
    $EDITOR $FACET_DIR/$(-facet-project $1)/facet.yaml
}

facet-workon () {
    FACET_PROJECT=$1
}

facet-current () {
    -facet-assert-current-project || return 1
    echo $FACET_PROJECT
}

facet-git-checkout () {
    cd ~/src/counsyl/website && git checkout $(facet-git-branch $1)
}

facet-git-branch () {
    facet-config $(-facet-project $1) | y2j | jq -r .branch
}

facet-jira-open () {
    open -a "/Applications/Google Chrome.app" https://jira.counsyl.com/browse/$(-facet-project $1)
}

facet-jira-json-fetch () {
    [ -n "$username" ] && [ -n "$password" ] || {
        echo "Missing environment variables 'username' and 'password'" 1>&2
        return 1
    }
    local project=$(-facet-project $1)
    local file=$(-facet-jira-json-file $project)
    curl -s https://$username:$password@jira.counsyl.com/rest/api/latest/issue/$project > $file
    echo $file
}

facet-jira-json () {
    local project=$(-facet-project $1)
    shift
    local file=$(-facet-jira-json-file $project)
    [ -e $file ] || facet-jira-json-fetch $project
    cat $file
}

facet-jira-summary () {
    facet-jira-json $(-facet-project $1) | jq -C .fields.summary
}

facet-config () {
    cat $FACET_DIR/$(-facet-project $1)/facet.yaml
}

facet-for-each () {
    for facet in $(facet-ls); do
        echo -n "$facet "
        $@ $facet
    done
}


# Etc

y2j () {
    python -c "import json, sys, yaml; print(json.dumps(yaml.load(sys.stdin), indent=2))"
}


# Private

-facet-project () {
    local project=$1
    [ -n "$project" ] || project=$FACET_PROJECT
    -facet-assert-valid-project "$project" || return 1
    echo $project
}

-facet-jira-json-file () {
    echo $FACET_DIR/$(-facet-project $1)/jira.json
}

-facet-assert-current-project () {
    [[ -n $FACET_PROJECT ]] || {
        echo "FACET_PROJECT is not set" 1>&2
        return 1
    }
    return 0
}

-facet-assert-valid-project () {
    [ -n "$1" ] || {
        echo "project variable is empty" 1>&2
        return 1
    }
    [ -d $FACET_DIR/$1 ] || {
        echo "Not a facet project: $1" 1>&2
        return 1
    }
    return 0
}


-facet-assert-not-valid-project () {
    [ -n "$1" ] || {
        echo "project variable is empty" 1>&2
        return 1
    }
    [ -d $FACET_DIR/$1 ] && {
        echo "Already a facet project: $1" 1>&2
        return 1
    }
    return 0
}


# Completion

-facet-complete-projects() {
    local input=${COMP_WORDS[COMP_CWORD]}
    local completions=$(ls $FACET_DIR | tr '\n' ' ')
    COMPREPLY=( $(compgen -W "$completions" -- $input) )
}
complete -F -facet-complete-projects facet-workon
complete -F -facet-complete-projects facet-jira-fetch
complete -F -facet-complete-projects -- -facet-project
complete -F -facet-complete-projects facet-config-edit
complete -F -facet-complete-projects facet-jira-open
complete -F -facet-complete-projects facet-jira-json
complete -F -facet-complete-projects facet-jira-json-fetch
complete -F -facet-complete-projects facet-jira-summary
complete -F -facet-complete-projects facet-config
