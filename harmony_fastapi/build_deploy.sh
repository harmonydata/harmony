#az login
#az acr login --name regprotocolsfds
rm -rf harmony
cp -r ../harmony_pypi_package/src/harmony/ ./
export COMMIT_ID=`git show -s --format=%ci_%h | sed s/[^_a-z0-9]//g | sed s/0[012]00_/_/g`
docker build -t harmonyapi --build-arg COMMIT_ID=$COMMIT_ID .
docker tag harmonyapi regprotocolsfds.azurecr.io/harmonyapi:$COMMIT_ID
docker push regprotocolsfds.azurecr.io/harmonyapi:$COMMIT_ID
echo "The container version is $COMMIT_ID"