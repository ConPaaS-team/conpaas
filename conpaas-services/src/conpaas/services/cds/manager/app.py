import os


def read_apps(apps_dir):
    apps = {}
    for app_file in os.listdir(apps_dir):
        path = os.path.join(apps_dir, app_file)
        with open(path) as f:
            content = f.readline()
            details = {}
            for part in content.split():
                (attr, value) = part.split('=')
                details[attr] = value
                details['mtime'] = os.path.getmtime(path)
            apps[app_file] = details
    return apps
