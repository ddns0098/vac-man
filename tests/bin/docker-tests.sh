#!/usr/bin/env sh

#set -eu

main() {
  log "INFO: Building vac-man:testing image ..."
  docker build -t vac-man:testing .

  log "INFO: Starting test container"
  docker run -it -e SECRET_KEY=$SECRET_KEY \
  -e GOOGLE_ID=$GOOGLE_ID \
  -e GOOGLE_SECRET=$GOOGLE_SECRET \
  -e SQLALCHEMY_DATABASE_URI=$SQLALCHEMY_DATABASE_URI \
  vac-man:testing \
  /src/vac_man/tests/bin/tests.sh "$@"
}

log() {
    printf "\n%s\n" "$@" >&2
}

main "$@"
