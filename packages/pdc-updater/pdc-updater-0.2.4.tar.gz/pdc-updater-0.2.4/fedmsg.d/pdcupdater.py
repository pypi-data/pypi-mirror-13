
import commands

config = {
    # Should we turn on the realtime updater?
    'pdcupdater.enabled': True,

    # Credentials to talk to PDC
    'pdcupdater.pdc': {
        #'server': 'https://pdc.fedorainfracloud.org/rest_api/v1/',
        #'insecure': True,
        #'token': 'b2c0c9f78e42e7af21bf4314bd016ed456c62f5e',
        'server': 'https://pdc.fedoraproject.org/rest_api/v1/',
        'insecure': False,
        'token': '13390697f0cce8f07e3b171a9d36da22ea1c70d8',
    },

    # Credentials to talk to FAS
    'pdcupdater.fas': {
        'base_url': 'https://admin.fedoraproject.org/accounts',
        'username': 'ralph',
        'password': commands.getoutput('pass sys/fas'),
    },

    # PkgDB details
    'pdcupdater.pkgdb_url': 'https://admin.fedoraproject.org/pkgdb',

    # Koji details
    'pdcupdater.koji_url': 'http://koji.fedoraproject.org/kojihub',

    # Where to find composes
    'pdcupdater.old_composes_url': 'https://kojipkgs.fedoraproject.org/compose/',

    # We have an explicit list of these in the config so we can turn them on
    # and off individually in production if one is causing an issue.
    'pdcupdater.handlers': [
        #'pdcupdater.handlers.pkgdb:NewPackageHandler',
        #'pdcupdater.handlers.pkgdb:NewPackageBranchHandler',
        #'pdcupdater.handlers.rpms:NewRPMHandler',
        #'pdcupdater.handlers.persons:NewPersonHandler',
        'pdcupdater.handlers.compose:NewComposeHandler',
        #'pdcupdater.handlers.atomic:AtomicComponentGroupHandler',
    ],

    'logging': dict(
        loggers=dict(
            pdcupdater={
                "level": "DEBUG",
                "propagate": False,
                "handlers": ["console"],
            },
            requests={
                "level": "INFO",
                "propagate": False,
                "handlers": ["console"],
            },
        )
    )
}
