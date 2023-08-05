from dictremapper import Remapper, Path


def get_fullname(repository):
    if "://" in repository:
        url = repository
        return "/".join(url.rstrip("/").split("/")[-2:])
    return repository


class Namespace(object):
    baseurl = "https://api.github.com"

    def __init__(self, fullname):
        self.fullname = fullname  # fullname is ":owner/:name"

    @property
    def versions_url(self):
        urlfmt = "{self.baseurl}/repos/{self.fullname}/tags"
        return urlfmt.format(self=self)

    @property
    def summary_url(self):
        urlfmt = "{self.baseurl}/repos/{self.fullname}"
        return urlfmt.format(self=self)


class SummaryRemapper(Remapper):
    name = Path("full_name")
    url = Path("html_url")
    description = Path("description")
    created_at = Path("created_at")
    updated_at = Path("updated_at")
    star = Path("stargazers_count")
