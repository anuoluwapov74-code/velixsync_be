class AppendSlashMiddleware:
    """
    Ensures all incoming requests have a trailing slash before URL resolution.
    This prevents Django's CommonMiddleware from attempting a redirect on POST
    requests that arrive without a trailing slash (e.g. when proxied via Next.js).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path_info.endswith("/"):
            request.path_info += "/"
            request.path += "/"
        return self.get_response(request)
