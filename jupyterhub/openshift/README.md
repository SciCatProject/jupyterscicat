# Jupyterhub deployment in Openshift

The following is based on the code in https://github.com/jupyter-on-openshift/jupyterhub-quickstart . You need to have a running openshift cluster with support for persistent volumes

## Preparing the SciCat Jupyter images

This includes the necessary python packages as well as the notebook, lab and voila based servers

* create initial image stream

```
oc create -f https://raw.githubusercontent.com/jupyter-on-openshift/jupyter-notebooks/master/image-streams/s2i-minimal-notebook.json
```
* build the scicat-notebook image

```
cd jupyterhub/openshift/
# if source is available locally or not yet committed
oc start-build scicat-notebook --from-dir=.

# if source is already in repo
oc new-build . --name scicat-notebook   --image-stream s2i-minimal-notebook:3.6   --context-dir scicat-notebook
```

## Installation of the Jupyer Hub

* Load the template

```
oc apply -f https://raw.githubusercontent.com/jupyter-on-openshift/jupyterhub-quickstart/master/templates/jupyterhub-workspace.json
```

* Use the template with site specific configuration parameters

For this you need to edit the jupyterhub_config.py to match your environment .Typically you need to modify the authentication settings, e.g. LDAP parameters.

Then run the following command:

```
oc new-app --template jupyterhub-workspace --param NOTEBOOK_MEMORY=2Gi --param CLUSTER_SUBDOMAIN=apps.ocp4a.psi.ch --param SPAWNER_NAMESPACE=`oc project --short` --param VOLUME_SIZE=4Gi --param IDLE_TIMEOUT=3600 --param JUPYTERHUB_CONFIG="`cat jupyterhub_config.py`" --param NOTEBOOK_IMAGE=scicat-notebook:latest
```

This will take a few minutes to finish. Afterwards you can enter the given URL address in a browser  which should start a login page into the Jupyter univers.

The initial startup of the server, which are created for each user may take some time (about 1 minute), subsequent logins are much faster.

If you have PVCs setup the data of the users is not lost when the PODS are recreated.

