"""
Documint action factories.

Each public function produces a `dict` suitable for passing to the
`perform_action` session method.
"""


def _action(name, params):
    """
    Convenience function for constructing an action `dict`.
    """
    return {u'action': name,
            u'parameters': params}


def render_html(input, base_uri=None):
    """
    Render an HTML document to a PDF document.

    :param unicode input: URI to the HTML content to render.
    :param base_uri: Optional base URI to use when resolving relative URIs.
    :type base_uri: unicode or None
    """
    params = {u'input': input}
    if base_uri is not None:
        params[u'base-uri'] = base_uri
    return _action(u'render_html', params)


def concatenate(inputs):
    """
    Concatenate several PDF documents together.

    :param inputs: Document URIs.
    :type inputs: list of unicode
    """
    return _action(u'concatenate',
                   {u'inputs': inputs})


def thumbnails(input, breadth):
    """
    Generate JPEG thumbnails for a PDF document.

    :param unicode input: Document URI.
    :param int breadth: Widest part of the thumbnail in pixels.
    """
    return _action(u'thumbnails',
                   {u'input': input,
                    u'breadth': breadth})


def split(input, page_groups):
    """
    Split a PDF document into multiple PDF documents.

    :param unicode input: Document URI.
    :param page-groups: Page number groups, each group of pages represents a
    new document containing only those pages from the original document in the
    order they are specified. For example ``[[1, 3, 2], [4, 2]]`` produces two
    documents: one with pages 1, 3 and 2; the other with pages 4 and 2.
    :type page-groups: list of lists of int
    """
    return _action(u'split',
                   {u'input': input,
                    u'page-groups': page_groups})


def metadata(input):
    """
    Retrieve metadata from a PDF document.

    :param unicode input: Document URI.
    """
    return _action(u'metadata',
                   {u'input': input})


def sign(inputs, certificate_alias, location, reason):
    """
    Digitally sign one or more PDF documents.

    :param inputs: Document URIs.
    :type inputs: list of unicode
    :param unicode certificate_alias: Certificate alias, in the Documint
    keystore, to use when signing the documents.
    :param unicode location: Signing location.
    :param unicode reason: Signing reason.
    """
    return _action(u'sign',
                   {u'inputs': inputs,
                    u'certificate-alias': certificate_alias,
                    u'location': location,
                    u'reason': reason})


def crush(input, compression_profile):
    """
    Compress a PDF document according to a specific compression profile.

    :param unicode input: Document URI.
    :param unicode compression_profile: Compression profile to use, possible
    choices are: ``text`` (bilevel), ``photo-grey`` (greyscale), ``photo``
    (colour).
    """
    return _action(u'crush',
                   {u'input': input,
                    u'compression-profile': compression_profile})
