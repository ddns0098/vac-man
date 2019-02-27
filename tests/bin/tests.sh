#!/usr/bin/env sh

set -eu

main() {

  log "INFO: Cleaning pyc..."
  find . -type d -name __pycache__ -exec rm -rf {} \; || true
  find . -type f -name '*.pyc' -delete

  log "INFO: Running tests ..."
  python setup.py develop
  pytest tests/pytest --exitfirst

  log "INFO: Running pylint ..."
  #pylint --rcfile tests/.pylintrc flaskr

  log "INFO: Running pycodestyle ..."
  #pycodestyle --max-line-length=150 --ignore=E402 flaskr
}

log() {
    printf "\n%s\n" "$@" >&2
}

main "$@"
