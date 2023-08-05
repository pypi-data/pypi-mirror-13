from pyramid.interfaces import ISessionFactory
from pyramid.settings import asbool


# ==============================================================================


class ISessionHttpsFactory(ISessionFactory):
    """
    subclass of ISessionFactory; needs to be unique class
    """
    pass


class NotHttpsRequest(Exception):
    """
    Raised when we're not an HTTPS request, and the application is configured 
    to ensure_scheme.
    """
    pass


# ------------------------------------------------------------------------------


def request_property__session_https(request):
    """
    Private Method.
    This should be a reified request method. 
    Note that we don't automatically raise a `NotHttpsRequest`.  
    This behavior is intentional.
    """
    # are we ensuring https?
    if request.registry.settings['pyramid_https_session_core.ensure_scheme']:
        if request.scheme != 'https':
            return None
            # don't raise yet, because it has issues with checking for session_https
            raise NotHttpsRequest()
    factory = request.registry.queryUtility(ISessionHttpsFactory)
    if factory is None:
        raise AttributeError('No `session_https` factory registered')
    return factory(request)


# ------------------------------------------------------------------------------


def register_https_session_factory(config, settings, https_session_factory):
    """
    Plugin Developer Method.
    Developers should call this when creating an ISessionHttpsFactory
    """
    
    def register_session_https_factory():
        config.registry.registerUtility(https_session_factory, ISessionHttpsFactory)

    intr = config.introspectable('session https factory',
                                 None,
                                 config.object_description(https_session_factory),
                                 'session https factory'
                                 )
    intr['factory'] = https_session_factory
    config.action(ISessionHttpsFactory, register_session_https_factory,
                  introspectables=(intr, ),
                  )
    config.set_request_property(request_property__session_https,
                                'session_https', reify=True,
                                )

# ------------------------------------------------------------------------------


class SessionBackendConfigurator(object):
    """
    A class that exposes some interfaces used to standardize implementations.
    
    A reference implementation is available in pyramid_https_session_redis
    
    * `https://github.com/jvanasco/pyramid_https_session_redis`
    """

    compatibility_options = {'secure': 'secure',
                             'httponly': 'httponly',
                             }
    """
    ``compatibility_options`` is a dict where the Keys are the names that
    "pyramid_https_sessions_core" expects for an option, and the Values are
    the names that the backend has elected.
    
    At a minimum, this must define `secure` and `httponly`
    """

    allowed_passthrough_options = ()
    """
    ``allowed_passthrough_options`` is a tuple of options that are allowed to
    passthrough to the backend constructor.  they will not be removed by any
    calls to `cleanup_options`.
    """
    
    @classmethod
    def ensure_compatibility(cls, factory_options):
        """
        Plugin Developer Method.
    
        This manipulates a dictionary `factory_options` in-place, ensuring any 
        commonly used attributes from one backend that are missing can be found
        in another backend.  This aids in adapting between 2 session backends.

        ``compatibility_options`` - a list of tuples where the first element is the 
        attribute name that the backend package uses to describe a given feature, 
        and the second element is the name used by legacy packages.

            compatibility_options = {'key': 'cookie_name',
                                     'domain': 'cookie_domain',
                                     'path': 'cookie_path',
                                     'secure': 'cookie_secure',
                                     'set_on_exception': 'cookie_on_exception',
                                     }

    
        ``factory_options`` - the dict of options to-be-passed to the factory
        """
        for standardized_k, backend_k in cls.compatibility_options.items():
            if (backend_k not in factory_options) and (standardized_k in factory_options):
                factory_options[backend_k] = factory_options.pop(standardized_k)

    @classmethod
    def ensure_security(cls, config, factory_options):
        """This ensures we do everything on https"""
        for _opt in ('secure',
                     'httponly',
                     ):
            # grab the backend version of the option
            _opt_backend = cls.compatibility_options[_opt]
            if _opt_backend in factory_options and not factory_options[_opt_backend]:
                raise ValueError("`%s` MUST be `True`" % _opt_backend)

        # note if we're going to ensure the https scheme... default to True
        ensure_scheme = True
        # extend this to our backend pyramid_https_session_core.ensure_scheme
        config.registry.settings['pyramid_https_session_core.ensure_scheme'] = ensure_scheme

        # force secure...
        for _opt in ('secure',
                     'httponly',
                     ):
            # grab the backend version of the option
            _opt_backend = cls.compatibility_options[_opt]
            factory_options[_opt_backend] = True

    @classmethod
    def cleanup_options(cls, factory_options):
        """clears out `pyramid_https_session_core` options"""
        # and remove the `pyramid_https_session_core` kwargs:
        for _opt in ('framework', 
                     'type',
                     'ensure_scheme',
                     ):
            if _opt in cls.allowed_passthrough_options:
                continue
            if _opt in factory_options:
                del factory_options[_opt]

    @classmethod
    def recast_options(cls, factory_options, prefix):
        return {"%s.%s" % (prefix, k): v for (k, v) in factory_options.items()}


