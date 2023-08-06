"""
Version checking utilities
"""

## Check for an update of the notifier
def get_repo_version():
    """
    Get the current version on GitHub
    """
    url = 'https://raw.githubusercontent.com/aquatix/ns-notifications/master/VERSION'
    response = requests.get(url)
    if response.status_code == 404:
        return None
    else:
        return response.text.replace('\n', '')


def get_local_version():
    """
    Get the locally installed version
    """
    with open ("VERSION", "r") as versionfile:
        return versionfile.read().replace('\n', '')


def check_versions(mc):
    """
    Check whether version of ns-notifier is up-to-date and ns-api is latest version too
    """
    message = {'header': 'ns-notifications needs updating', 'message': None}
    current_version = None
    version = mc.get('ns-notifier_version')
    if not version:
        version = get_repo_version()
        current_version = get_local_version()
        if version != current_version:
            message['message'] = 'Current version: ' + str(current_version) + '\nNew version: ' + str(version)
            mc.set('ns-notifier_version', version, MEMCACHE_VERSIONCHECK_TTL)

    version = mc.get('ns-api_version')
    if not version:
        if ns_api.__version__ != VERSION_NSAPI:
            # ns-api needs updating
            if message['message']:
                message['message'] = message['message'] + '\n'
            else:
                message['message'] = ''
            message['message'] = message['message'] + 'ns-api needs updating'
            mc.set('ns-api_version', VERSION_NSAPI, MEMCACHE_VERSIONCHECK_TTL)

    if not message['message']:
        # No updating needed, return None object
        message = None
    return message
