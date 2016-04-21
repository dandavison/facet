#!/bin/bash -eu

export FACET_DIR=~/.facets

facet-workon () {
    FACET_CURRENT_PROJECT=$1
}

facet-current () {
    -facet-assert-current-project || return 1
    echo $FACET_CURRENT_PROJECT
}

facet-jira-open () {
    -facet-assert-current-project || return 1
    open -a "/Applications/Google Chrome.app" https://jira.counsyl.com/browse/$FACET_CURRENT_PROJECT
}

facet-jira-issue-json () {
    -facet-assert-current-project || return 1
    curl -s https://$username:$password@jira.counsyl.com/rest/api/latest/issue/$FACET_CURRENT_PROJECT
}

facet-jira-summary () {
    facet-jira-issue-json | jq -C .fields.summary
}

# Completion

-facet-workon-complete() {
    local input=${COMP_WORDS[COMP_CWORD]}
    local completions=$(ls $FACET_DIR | tr '\n' ' ')
    COMPREPLY=( $(compgen -W "$completions" -- $input) )
}
complete -F -facet-workon-complete facet-workon


# Private

-facet-assert-current-project () {
    [[ -z $FACET_CURRENT_PROJECT ]] && {
        echo "FACET_CURRENT_PROJECT is not set" >&2
        return 1
    }
    return 0
}
