#!/bin/sh

# We need to stop minio after it's done re-keying. To this end, we use the expect package
apk add expect --no-cache

#We need to make sure the current credentials are not working...
RESULT="$(expect -c 'spawn /usr/bin/minio server /data; expect "SecretKey:";')"
if [[ $(echo $RESULT | grep -c $MINIO_SECRET_KEY) -gt 0 ]]; then
    echo "Credentials already updated, nothing to do here!"
    exit 1
fi

# ..but the old ones are
RESULT="$(MINIO_SECRET_KEY=$MINIO_SECRET_KEY_OLD expect -c 'spawn /usr/bin/minio server /data; expect "SecretKey:";')"
if [[ $(echo $RESULT | grep -c $MINIO_SECRET_KEY_OLD) -eq 0 ]]; then
    echo "Invalid old credentials!"
    exit 1
fi

export MINIO_ACCESS_KEY_OLD="$MINIO_ACCESS_KEY" MINIO_SECRET_KEY_OLD="$MINIO_SECRET_KEY_OLD"
RESULT="$(expect -c 'spawn /usr/bin/minio server /data; expect "SecretKey:";')"
if [[ $(echo $RESULT | grep -c "$MINIO_SECRET_KEY") -eq 0 ]]; then
    echo "Unexpected error occurred during MinIO secret key rotation"
    expect -c 'spawn /usr/bin/minio server /data; { close; exit 1} "'
    exit 1
fi

echo "Minio server key rotation completed"
exit 0
