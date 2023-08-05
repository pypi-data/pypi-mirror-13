import pdcupdater.handlers
import pdcupdater.services
import pdcupdater.utils

from pdc_client import get_paged

import logging

log = logging.getLogger(__name__)


def collection2release_id(pdc, collection):
    # Silly rawhide.  We don't know what number you are...
    if collection['version'] == 'devel':
        collection['version'] = collection['dist_tag'].split('fc')[-1]
        release_type = 'ga'
        template = "{short}-{version}"
    else:
        release_type = 'updates'
        template = "{short}-{version}-updates"

    # lowercase this for the prefix.
    release = {
        'name': collection['name'],
        'short': collection['name'].lower().split()[-1],
        'version': collection['version'],
        'release_type': release_type,
    }
    release_id = template.format(**release)
    pdcupdater.utils.ensure_release_exists(pdc, release_id, release)
    return release_id


class NewPackageHandler(pdcupdater.handlers.BaseHandler):
    """ When a new package gets added to pkgdb. """

    def __init__(self, *args, **kwargs):
        super(NewPackageHandler, self).__init__(*args, **kwargs)
        self.pkgdb_url = self.config['pdcupdater.pkgdb_url']

    @property
    def topic_suffixes(self):
        return ['pkgdb.package.new']

    def can_handle(self, msg):
        return msg['topic'].endswith('pkgdb.package.new')

    def handle(self, pdc, msg):
        name = msg['msg']['package_name']
        branch = msg['msg']['package_listing']['collection']['branchname']
        collection = msg['msg']['package_listing']['collection']
        release_id = collection2release_id(pdc, collection)
        global_component = name
        data = dict(
            name=name,
            release=release_id,
            global_component=global_component,
            dist_git_branch=branch,
            #bugzilla_component=name,
            brew_package=name,
            active=True,
            type='rpm',
        )
        pdcupdater.utils.ensure_global_component_exists(pdc, name)
        # https://pdc.fedorainfracloud.org/rest_api/v1/release-components/
        log.info("Creating release component %s for %s" % (name, release_id))
        pdc['release-components']._(data)

    def audit(self, pdc):
        packages = pdcupdater.services.pkgdb_packages(self.pkgdb_url)
        pdc_pkgs = get_paged(pdc['global-components']._)

        # normalize the two lists
        pkg_package = set([p['name'] for p in packages])
        pdc_package = set([p['name'] for p in pdc_pkgs])

        # use set operators to determine the difference
        present = pdc_package - pkg_package
        absent = pkg_package - pdc_package

        return present, absent

    def initialize(self, pdc):
        packages = pdcupdater.services.pkgdb_packages(self.pkgdb_url)
        bulk_payload = [dict(
            name=package['name'],
        ) for package in packages]
        pdc['global-components']._(bulk_payload)


class NewPackageBranchHandler(pdcupdater.handlers.BaseHandler):
    """ When a new package gets a new branch in pkgdb. """

    def __init__(self, *args, **kwargs):
        super(NewPackageBranchHandler, self).__init__(*args, **kwargs)
        self.pkgdb_url = self.config['pdcupdater.pkgdb_url']

    @property
    def topic_suffixes(self):
        return ['pkgdb.package.branch.new']

    def can_handle(self, msg):
        return msg['topic'].endswith('pkgdb.package.branch.new')

    def handle(self, pdc, msg):
        name = msg['msg']['package_listing']['package']['name']
        branch = msg['msg']['package_listing']['collection']['branchname']
        collection = msg['msg']['package_listing']['collection']
        release_id = collection2release_id(pdc, collection)
        global_component = name
        data = dict(
            name=name,
            release=release_id,
            global_component=global_component,
            dist_git_branch=branch,
            #bugzilla_component=name,
            brew_package=name,
            active=True,
            type='rpm',
        )
        # https://pdc.fedorainfracloud.org/rest_api/v1/release-components/
        pdcupdater.utils.ensure_global_component_exists(pdc, name)
        log.info("Creating release component %s for %s" % (name, release_id))
        pdc['release-components']._(data)

    def audit(self, pdc):
        packages = pdcupdater.services.pkgdb_packages(
            self.pkgdb_url, extra=True)
        pdc_pkgs = get_paged(pdc['release-components']._)

        # normalize the two lists
        pkg_package = set(
            (
                package['name'],
                collection['koji_name'],
                collection['branchname']
            )
            for package in packages
            for collection in package['collections']
        )
        pdc_package = set(
            (p['name'], p['release'], p['dist_git_branch'])
            for p in pdc_pkgs
        )

        # use set operators to determine the difference
        present = pdc_package - pkg_package
        absent = pkg_package - pdc_package

        return present, absent

    def initialize(self, pdc):
        packages = pdcupdater.services.pkgdb_packages(
            self.pkgdb_url, extra=True)
        bulk_payload = [
            dict(
                name=package['name'],
                release=collection2release_id(pdc, collection),
                global_component=package['name'],
                dist_git_branch=collection['branchname'],
                #bugzilla_component=package['name'],
                brew_package=package['name'],
                active=True,
                type='rpm',
            )
        for package in packages
        for collection in package['collections']
        ]

        pdc['release-components']._(bulk_payload)
