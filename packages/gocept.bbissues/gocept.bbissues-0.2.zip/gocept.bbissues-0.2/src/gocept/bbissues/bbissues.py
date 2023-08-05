import requests
from jinja2 import Template
import ConfigParser
import logging
import dateutil.parser
import pkg_resources
import argparse


log = logging.getLogger('bbissues')


parser = argparse.ArgumentParser(
    description='Collect issues from bitbucket issue trackers.')
parser.add_argument('--config', dest='config_path', help='Config file.',
                    required=True)

DEFAULT_TEMPLATE = pkg_resources.resource_string(
    'gocept.bbissues', 'index.jj2')


def timefmt(timestr):
    return dateutil.parser.parse(timestr).strftime('%Y-%m-%d %H:%M')


class Base(object):

    issue_base_url = NotImplemented
    pullrequest_base_url = NotImplemented
    web_base_url = NotImplemented

    def __init__(self, projects):
        self.projects = projects.split()

    def __call__(self):
        for owner, project in [p.split(':') for p in self.projects]:
            issuedata = self.collect_project_issues(owner, project)
            prdata = self.collect_project_pullrequests(owner, project)
            if issuedata or prdata:
                yield dict(
                    name=project,
                    issues=issuedata,
                    pullrequests=prdata)

    def get_error_message(self, data):
        raise NotImplementedError()

    def get_json(self, url):
        try:
            result = requests.get(url)
            if not result.ok:
                error = self.get_error_message(result.json())
                log.warn('Error while calling {}: {}'.format(url, error))
                return
        except requests.ConnectionError:
            log.warn('Connection error while calling {}'.format(url))
            return
        return result.json()


class Bitbucket(Base):

    issue_base_url = ('https://api.bitbucket.org/1.0/repositories/{}/{}/'
                      'issues?status=!resolved')
    pullrequest_base_url = ('https://api.bitbucket.org/2.0/repositories/{}/{}'
                            '/pullrequests')
    web_base_url = 'https://bitbucket.org/{}'

    def get_error_message(self, data):
        return data['error']['message']

    def collect_project_pullrequests(self, owner, project):
        prs = self.get_json(self.pullrequest_base_url.format(owner, project))
        data = []
        if prs is None:
            return []
        for pr in prs['values']:
            if pr['state'] != 'OPEN':
                continue
            prdata = dict(
                title=pr['title'],
                content=pr['description'].strip(),
                status=pr['state'],
                created=timefmt(pr['created_on']),
                priority='pullrequest',
                prioclass=self.prioclass('normal'),
                url=self.web_base_url.format(
                    '{}/{}/pull-requests/{}'.format(owner, project, pr['id'])),
                author=pr['author']['display_name'])
            data.append(prdata)
        return data

    def prioclass(self, prio):
        return dict(minor='warning',
                    major='danger',
                    normal='primary').get(prio, 'default')

    def collect_project_issues(self, owner, project):
        issues = self.get_json(self.issue_base_url.format(owner, project))
        if issues is None:
            return []
        data = []
        for issue in issues['issues']:
            issuedata = dict(
                title=issue['title'],
                content=issue['content'].strip(),
                status=issue['status'],
                created=timefmt(issue['created_on']),
                priority=issue['priority'],
                prioclass=self.prioclass(issue['priority']),
                url=self.web_base_url.format(issue['resource_uri'][18:]),
                author=issue['reported_by']['display_name'])
            data.append(issuedata)
        return data


class Github(Base):

    issue_base_url = 'https://api.github.com/repos/{}/{}/issues'
    pullrequest_base_url = 'https://api.github.com/repos/{}/{}/pulls'

    def get_error_message(self, data):
        return data['message']

    def collect_data(self, url):
        issues = self.get_json(url)
        for issue in issues:
            yield dict(
                title=issue['title'],
                content=issue['body'].strip(),
                status=issue['state'],
                created=timefmt(issue['created_at']),
                priority=None,
                prioclass=None,
                url=issue['html_url'],
                author=issue['user']['login'])

    def collect_project_issues(self, owner, project):
        return list(self.collect_data(
            self.issue_base_url.format(owner, project)))

    def collect_project_pullrequests(self, owner, project):
        return list(self.collect_data(
            self.pullrequest_base_url.format(owner, project)))


def main():
    args = parser.parse_args()
    config = ConfigParser.ConfigParser()
    config.read(args.config_path)
    try:
        custom_template = config.get('config', 'template_path')
        with open(custom_template) as templatefile:
            template_content = templatefile.read()
    except ConfigParser.NoOptionError:
        template_content = DEFAULT_TEMPLATE
    template = Template(template_content)
    logging.basicConfig(
        filename=config.get('config', 'log'), level=logging.WARNING)
    projectsdata = []

    projects = config.get('bitbucket', 'projects')
    projectsdata.extend(Bitbucket(projects)())

    projects = config.get('github', 'projects')
    projectsdata.extend(Github(projects)())

    result = template.render(projects=projectsdata)
    print result


if __name__ == '__main__':
    main()
