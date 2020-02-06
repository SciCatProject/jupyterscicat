# Set the log level by value or name.
#c.JupyterHub.log_level = 'DEBUG'
# Enable debug-logging of the single-user server
#c.Spawner.debug = True
# Enable debug-logging of the single-user server
#c.KubeSpawner.debug = True

c.KubeSpawner.start_timeout = 560
c.KubeSpawner.http_timeout = 440
c.KubeSpawner.storage_capacity = '4Gi'
c.KubeSpawner.environment = { 'JUPYTER_ENABLE_LAB': 'false' }
c.JupyterHub.authenticator_class = 'ldapauthenticator.LDAPAuthenticator'

c.JupyterHub.services = [
    {
      'name': 'cull-idle',
      'admin': True,
      'command': ['cull-idle-servers', '--timeout=7200'],
    }
]

c.LDAPAuthenticator.server_address = 'd.psi.ch'
c.LDAPAuthenticator.server_port = 389
c.LDAPAuthenticator.bind_dn_template = 'CN={username},ou=users,ou=psi,dc=d,dc=psi,dc=ch'
c.LDAPAuthenticator.lookup_dn = True
c.LDAPAuthenticator.lookup_dn_search_filter = '({login_attr}={login})'
c.LDAPAuthenticator.lookup_dn_search_user = 'add your infos here... '
c.LDAPAuthenticator.lookup_dn_search_password = 'add your password here...'
c.LDAPAuthenticator.user_search_base = 'ou=PSI,dc=d,dc=psi,dc=ch'
c.LDAPAuthenticator.user_attribute = 'sAMAccountName'
c.LDAPAuthenticator.lookup_dn_user_dn_attribute = 'cn'
c.LDAPAutheticator.use_lookup_dn_username = True
c.LDAPAuthenticator.escape_userdn = False

# update hook to make it work with ldap (remove oauth specific part)

@gen.coroutine
def my_modify_pod_hook(spawner, pod):
    pod.spec.automount_service_account_token = True

    # Grab the OpenShift user access token from the login state.

    # auth_state = yield spawner.user.get_auth_state()
    # access_token = auth_state['access_token']

    # Set the session access token from the OpenShift login.

    #pod.spec.containers[0].env.append(
    #        dict(name='OPENSHIFT_TOKEN', value=access_token))

    # See if a template for the project name has been specified.
    # Try expanding the name, substituting the username. If the
    # result is different then we use it, not if it is the same
    # which would suggest it isn't unique.

    project = os.environ.get('OPENSHIFT_PROJECT')

    if project:
        name = project.format(username=spawner.user.name)
        if name != project:
            pod.spec.containers[0].env.append(
                    dict(name='PROJECT_NAMESPACE', value=name))

            # Ensure project is created if it doesn't exist.

            pod.spec.containers[0].env.append(
                    dict(name='OPENSHIFT_PROJECT', value=name))

    return pod

c.KubeSpawner.modify_pod_hook = my_modify_pod_hook

# make only src subdirectory mounted on pvc. Needed to avoid 5 Min. startup

c.KubeSpawner.user_storage_pvc_ensure = True
# defined differently in default configuration c.KubeSpawner.pvc_name_template = '%s-nb-{username}' % c.KubeSpawner.hub_connect_ip
c.KubeSpawner.user_storage_capacity = '1Gi'
c.KubeSpawner.volumes = [
    {
        'name': 'data',
        'persistentVolumeClaim': {
            'claimName': c.KubeSpawner.pvc_name_template
        }
    }
]
c.KubeSpawner.volume_mounts = [
    {
        'name': 'data',
        'mountPath': '/opt/app-root/src'
    }
]

c.KubeSpawner.init_containers = []
