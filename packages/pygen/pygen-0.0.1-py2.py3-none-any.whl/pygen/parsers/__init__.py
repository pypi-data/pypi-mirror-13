"""
Common parser methods.
"""

import pkg_resources
import warnings
import requests
import mimetypes

from six.moves.urllib.parse import urlsplit

from ..exceptions import NoParserError


def get_parser_class_map():
    result = {}

    for entry_point in pkg_resources.iter_entry_points(
        group='pygen_parsers',
    ):
        try:
            class_ = entry_point.load()
        except ImportError as ex:
            warnings.warn(
                "Exception while loading pygen parser %r. It won't be "
                "available. Exception was: %s" % (entry_point.name, ex),
                RuntimeWarning,
            )
            continue

        for mimetype in class_.mimetypes:
            if mimetype in result:
                current_class = result[mimetype]

                if current_class != class_:
                    warnings.warn(
                        "Could not register mimetype %r with parser %r as it "
                        "is already registered with a different parser "
                        "(%r)." % (
                            mimetype,
                            class_,
                            current_class,
                        ),
                        RuntimeWarning,
                    )
            else:
                class_.register()
                result[mimetype] = class_

    return result


parser_class_map = get_parser_class_map()


def get_parser_for_type(mimetype):
    parser_class = parser_class_map.get(mimetype)

    if not parser_class:
        raise NoParserError(
            mimetype=mimetype,
            mimetypes=set(parser_class_map),
        )

    return parser_class()


def read_context_from_url(url):
    parts = urlsplit(url, scheme='file')

    if parts.scheme == 'file':
        mimetype, _ = mimetypes.guess_type(url)
        parser = get_parser_for_type(mimetype)

        with open(parts.path) as file:
            return parser.load(file)
    else:
        result = requests.get(url)
        mimetype = result.headers['Content-Type'].split(';')[0]
        parser = get_parser_for_type(mimetype)
        return parser.loads(result.text)
