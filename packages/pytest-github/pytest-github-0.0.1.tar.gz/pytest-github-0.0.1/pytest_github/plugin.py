"""
pytest-github is a plugin for py.test that allows tests to reference github issues for skip/xfail handling.

:copyright: see LICENSE for details
:license: MIT, see LICENSE for more details.
"""

import os
import logging
import yaml
import pytest
import py  # NOQA
import re
import github3
import warnings
from _pytest.resultlog import generic_path

# Import, or define, NullHandler
try:
    from logging import NullHandler
except ImportError:
    from logging import Handler

    class NullHandler(Handler):

        """NullHandler implementation for python 2.6."""

        def emit(self, record):
            """Fake emit method."""
            pass

log = logging.getLogger(__name__)
log.addHandler(NullHandler())

# Cache the github issues to reduce duplicate lookups
_issue_cache = {}

# Maintain a list of github labels to consider issues "finished".  Any issues
# associated with these labels will be considered "done".
GITHUB_COMPLETED_LABELS = []


def pytest_addoption(parser):
    """Add options to control github integration."""
    group = parser.getgroup('pytest-github')
    group.addoption('--github-cfg',
                    action='store',
                    dest='github_cfg_file',
                    default='github.yml',
                    metavar='GITHUB_CFG',
                    help='GitHub configuration file (default: %default)')
    group.addoption('--github-username',
                    action='store',
                    dest='github_username',
                    default=None,
                    metavar='GITHUB_USERNAME',
                    help='GitHub username (defaults to value supplied in GITHUB_CFG)')
    group.addoption('--github-api-token',
                    action='store',
                    dest='github_api_token',
                    metavar='GITHUB_API_TOKEN',
                    default=None,
                    help='GitHub Personal Access token (defaults to value ' +
                    'supplied in GITHUB_CFG). Refer to ' +
                    'https://github.com/blog/1509-personal-api-tokens')
    group.addoption('--github-completed',
                    action='append',
                    dest='github_completed',
                    metavar='GITHUB_COMPLETED',
                    default=[],
                    help='Any issues in GITHUB_COMPLETED will be treated as '
                    'done (default: %s)' % GITHUB_COMPLETED_LABELS)
    group.addoption('--github-summary',
                    action='store_true',
                    dest='show_github_summary',
                    default=False,
                    help='Show a summary of all GitHub markers and their associated tests')

    # Add github marker to --help
    parser.addini("github", "GitHub issue integration", "args")


def pytest_configure(config):
    """Validate --github-* parameters."""
    log.debug("pytest_configure() called")

    # Add marker
    config.addinivalue_line("markers", "github(*args): GitHub issue integration")

    # Sanitize key and token
    github_cfg_file = config.getoption('github_cfg_file')
    github_username = config.getoption('github_username')
    github_api_token = config.getoption('github_api_token')
    github_completed = config.getoption('github_completed')

    # If not --help or --collectonly or --showfixtures ...
    if not (config.option.help or config.option.showfixtures):
        # Warn if file does not exist
        if not os.path.isfile(github_cfg_file):
            errstr = "No github configuration file found matching: %s" % github_cfg_file
            log.warning(errstr)
            warnings.warn(errstr, Warning)

        # Load configuration file ...
        if os.path.isfile(github_cfg_file):
            with open(github_cfg_file, 'r') as fd:
                github_cfg = yaml.load(fd)
                try:
                    github_cfg = github_cfg.get('github', {})
                except AttributeError:
                    github_cfg = {}
                    errstr = "No github configuration found in file: %s" % github_cfg_file
                    log.warning(errstr)
                    warnings.warn(errstr, Warning)

            if github_username is None:
                github_username = github_cfg.get('key', None)
            if github_api_token is None:
                github_api_token = github_cfg.get('token', None)
            if github_completed is None or github_completed == []:
                github_completed = github_cfg.get('completed', [])

        # Initialize github api connection
        api = github3.login(github_username, github_api_token)

        # If completed is still empty, load default ...
        if github_completed is None or github_completed == []:
            github_completed = GITHUB_COMPLETED_LABELS

        # Register pytest plugin
        assert config.pluginmanager.register(
            GitHubPytestPlugin(api, completed_labels=github_completed),
            'github_helper'
        )


def pytest_cmdline_main(config):
    """Check show_fixture_duplicates option to show fixture duplicates."""
    log.debug("pytest_cmdline_main() called")
    if config.option.show_github_summary:
        from _pytest.main import wrap_session
        wrap_session(config, __show_github_summary)
        return 0


def __show_github_summary(config, session):
    """Generate a report that includes all linked GitHub issues, and their status."""
    # collect tests
    session.perform_collect()

    # For each item, collect github markers and a generic_path for the item
    issue_map = dict()
    for item in filter(lambda i: i.get_marker("github") is not None, session.items):
        marker = item.get_marker('github')
        issue_urls = tuple(sorted(set(marker.args)))  # (O_O) for caching
        for issue_url in issue_urls:
            if issue_url not in issue_map:
                issue_map[issue_url] = list()
            issue_map[issue_url].append(generic_path(item))

    # Print a summary report
    reporter = config.pluginmanager.getplugin("terminalreporter")
    reporter.section("github issue report")
    if issue_map:
        for issue_url, gpaths in issue_map.items():
            # FIXME - display the status
            reporter.write_line("{0}".format(issue_url), bold=True)
            for gpath in gpaths:
                reporter.write_line(" - %s" % gpath)
    else:
        reporter.write_line("No github issues collected")


class GitHubPytestPlugin(object):

    """GitHub Plugin class."""

    def __init__(self, api, **kwargs):
        """Initialize attributes."""
        log.debug("GitHubPytestPlugin initialized")
        self.api = api
        self.completed_labels = kwargs.get('completed_labels', [])

    def __parse_issue_url(self, url):
        # Parse the github URL
        match = re.match(r'https?://github.com/([^/]+)/([^/]+)/(?:issues|pull)/([0-9]+)$', url)
        if match is None:
            raise Exception("Unhandled github issue URL: %s" % url)
        return match.groups()

    def __cache_github_issues(self, items):
        """Collect github markers and populate the issue_cache."""
        for item in filter(lambda i: i.get_marker("github") is not None, items):
            marker = item.get_marker('github')
            issue_urls = tuple(sorted(set(marker.args)))  # (O_O) for caching
            for issue_url in issue_urls:
                if issue_url not in _issue_cache:
                    # parse the URL
                    (username, repository, number) = self.__parse_issue_url(issue_url)

                    try:
                        _issue_cache[issue_url] = self.api.issue(username, repository, number)
                    except AttributeError:
                        errstr = "Unable to inspect github issue %s" % issue_url
                        warnings.warn(errstr, Warning)
            item.funcargs["github_issues"] = issue_urls

    def pytest_runtest_setup(self, item):
        """Handle github marker by calling xfail or skip, as needed."""
        log.debug("pytest_runtest_setup() called")
        if 'github' not in item.keywords:
            return

        unresolved_issues = []
        issue_urls = item.funcargs["github_issues"]
        for issue_url in issue_urls:
            if issue_url not in _issue_cache:
                continue
                # warnings.warn(errstr, Warning)

            issue = _issue_cache[issue_url]

            issue_labels = [l.name for l in issue.labels()]

            # if the issue is open and isn't considered "completed" by any of the issue labels ...
            if not issue.is_closed() and not set(self.completed_labels).intersection(issue_labels):
                # consider it unresolved
                unresolved_issues.append(issue)

        if unresolved_issues:
            # TODO - Add support for skip vs xfail
            skip = item.get_marker('github').kwargs.get('skip', False)
            if False and skip:
                pytest.skip("Skipping due to unresolved github issues:\n{0}".format(
                    "\n ".join(["{0} [{1}] {2}".format(i.url, i.state, i.title) for i in unresolved_issues])))
            else:
                item.add_marker(pytest.mark.xfail(
                    reason="Xfailing due to unresolved github issues: \n{0}".format(
                        "\n ".join(["{0} [{1}] {2}".format(i.url, i.state, i.title) for i in unresolved_issues]))))

    def pytest_collection_modifyitems(self, session, config, items):
        """Report number of github issues collected."""
        log.debug("pytest_collection_modifyitems() called")
        reporter = config.pluginmanager.getplugin("terminalreporter")
        reporter.write("collected", bold=True)

        # cache the issues
        self.__cache_github_issues(items)

        reporter.write_line(" {0} github issues".format(len(_issue_cache)), bold=True)
