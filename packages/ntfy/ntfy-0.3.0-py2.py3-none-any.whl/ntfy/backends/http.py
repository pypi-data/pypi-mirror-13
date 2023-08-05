import requests


def notify(config, message='', subject='', device=''):
    """
    Required config keys:
        * 'url'
    Useful config keys:
        * 'mappings': should be a dictionary of dictoinaries. The keys in
        dictoinary are the keyword argument to the requests functoin. the
        dictionary that is it's value is used to populate a dictionary to be
        passed as that argument. the key is the key to be populated and the
        value is a py3k style format string that gets passed message, subject,
        device and **config as arguments.
        example:
            {
            'data': {'body': '{message}', 'title': '{subject}'},
            'headers': {'Access-Token': '{access_token}'},
            }
        * 'user_key'
    """

    kwargs = {}
    for arg, mapping in config.get('mappings', {}).items():
        kwargs[arg] = {key: value.format(message=message, subject=subject,
                                         device=device, **config)
                       for key, value in mapping}
        # drop keys with falsey values
        kwargs[arg] = {k: v for k,v in kwargs[arg].items() if v}

    resp = requests.post(config['url'], **kwargs)

    resp.raise_for_status()
