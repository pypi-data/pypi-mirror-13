from datetime import datetime, timedelta
from jinja2 import Template
import ConfigParser
import argparse
import dateutil.parser
import json
import logging
import pkg_resources
import requests


log = logging.getLogger('bbissues')


parser = argparse.ArgumentParser(
    description='Collect issues from bitbucket issue trackers.')
parser.add_argument('--config', dest='config_path', help='Config file.',
                    required=True)

DEFAULT_TEMPLATE_PATH = pkg_resources.resource_filename(
    'gocept.bbissues', 'index.jj2')


def timefmt(timestr):
    return dateutil.parser.parse(timestr).strftime('%Y-%m-%d %H:%M')


class Base(object):

    issue_base_url = NotImplemented
    pullrequest_base_url = NotImplemented
    web_base_url = NotImplemented

    def __init__(self, owner, projects=None):
        if projects:
            self.projects = projects.split()
        else:
            self.projects = self.collect_projects(owner)

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

    def collect_projects(self, owner):
        raise NotImplementedError()

    def get_json(self, url):
        try:
            result = requests.get(url)
            if not result.ok:
                error = self.get_error_message(result.json())
                log.warn('Error while calling {}: {}'.format(url, error))
                return []
        except requests.ConnectionError:
            log.warn('Connection error while calling {}'.format(url))
            return []
        return result.json()


class Bitbucket(Base):
    """ Bitbucket class"""

    projects_base_url = ('https://api.bitbucket.org/2.0/repositories'
                         '/{}?q=has_issues=true&pagelen=100')
    issue_base_url = ('https://api.bitbucket.org/1.0/repositories/{}/{}/'
                      'issues?status=new&status=open&status=on+hold')
    pullrequest_base_url = ('https://api.bitbucket.org/2.0/repositories/{}/{}'
                            '/pullrequests')
    web_base_url = 'https://bitbucket.org/{}'

    def get_error_message(self, data):
        return data['error']['message']

    def collect_projects(self, owner):
        projects = self.get_json(self.projects_base_url.format(owner))
        if projects is None:
            return []
        return ['{}:{}'.format(owner, project['name'])
                for project in projects['values']]

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
                author=pr['author']['display_name'],
                comment_count=self.get_comment_count(pr))
            data.append(prdata)
        return data

    def prioclass(self, prio):
        return dict(minor='warning',
                    major='danger',
                    normal='primary').get(prio, 'default')

    def get_comment_count(self, issue_data):
        comment_url = issue_data['links']['comments']['href']
        comment_data = self.get_json(comment_url)
        return comment_data['size']

    def collect_project_issues(self, owner, project):
        issues = self.get_json(self.issue_base_url.format(owner, project))
        if issues is None:
            return []
        data = []

        for issue in issues['issues']:
            if 'reported_by' not in issue:
                author = 'Anonym'
            else:
                author = issue['reported_by']['display_name']
            issuedata = dict(
                title=issue['title'],
                content=issue['content'].strip(),
                status=issue['status'],
                created=timefmt(issue['created_on']),
                priority=issue['priority'],
                prioclass=self.prioclass(issue['priority']),
                url=self.web_base_url.format(issue['resource_uri'][18:]),
                author=author,
                comment_count=issue['comment_count'])
            data.append(issuedata)
        return data


class Github(Base):

    projects_base_url = 'https://api.github.com/users/{}/repos'
    issue_base_url = 'https://api.github.com/repos/{}/{}/issues'
    pullrequest_base_url = 'https://api.github.com/repos/{}/{}/pulls'

    def get_error_message(self, data):
        return data['message']

    def collect_projects(self, owner):
        projects = self.get_json(self.projects_base_url.format(owner))
        if projects is None:
            return []
        return ['{}:{}'.format(owner, project['name'])
                for project in projects if project['has_issues']]

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
                author=issue['user']['login'],
                comment_count=issue['comments'])

    def collect_project_issues(self, owner, project):
        return list(self.collect_data(
            self.issue_base_url.format(owner, project)))

    def get_comment_count_pullrequest(self, pullrequest):
        pullrequest_comments_url = pullrequest['comments_url']
        pullrequest_comments = self.get_json(pullrequest_comments_url)
        return len(pullrequest_comments)

    def collect_project_pullrequests(self, owner, project):
        pullrequests = self.get_json(
            self.pullrequest_base_url.format(owner, project))
        if pullrequests is None:
            return []
        data = []
        for pr in pullrequests:
            pr_data = dict(
                title=pr['title'],
                content=pr['body'].strip(),
                status=pr['state'],
                created=timefmt(pr['created_at']),
                priority=None,
                prioclass=None,
                url=pr['html_url'],
                author=pr['user']['login'],
                comment_count=self.get_comment_count_pullrequest(pr))
            data.append(pr_data)
        return data


class Handler(object):

    def __init__(self):
        args = parser.parse_args()
        self.config = ConfigParser.ConfigParser()
        self.config.read(args.config_path)
        logging.basicConfig(
            filename=self.config.get('config', 'log'),
            level=logging.WARNING)
        self.projects = self.get_projects()
        self.time_rendered = datetime.now().strftime('%Y-%m-%d %H:%M')

    def get_config_option(self, option, section='config', default=None):
        try:
            return self.config.get(section, option)
        except ConfigParser.NoOptionError:
            return default

    def get_projects(self):
        result = []

        owner = self.get_config_option('owner', section='bitbucket')
        projects = self.get_config_option('projects', section='bitbucket')

        if owner and projects:
            result.extend(Bitbucket(owner, projects)())
        else:
            result.extend(Bitbucket(owner)())

        owner = self.get_config_option('owner', section='github')
        projects = self.get_config_option('projects', section='github')
        if owner and projects:
            result.extend(Github(owner, projects)())
        else:
            result.extend(Github(owner)())

        return result

    def export_html(self):
        export_path = self.get_config_option('html_export_path')
        if export_path is None:
            return
        template_path = self.get_config_option(
            'template_path', default=DEFAULT_TEMPLATE_PATH)
        with open(template_path) as templatefile:
            with open(export_path, 'w') as html_file:
                (Template(templatefile.read())
                 .stream(projects=self.projects,
                         time_rendered=self.time_rendered)
                 .dump(html_file))

    def export_json(self):
        export_path = self.get_config_option('json_export_path')
        if export_path is None:
            return
        days = int(self.get_config_option('json_export_days', default=60))

        result = []
        not_older_than = datetime.now() - timedelta(days=days)
        for project in self.projects:
            for item in project['issues'] + project['pullrequests']:
                created = dateutil.parser.parse(item['created'])
                if created < not_older_than:
                    continue
                result.append(dict(
                    project=project['name'],
                    title=item['title'],
                    author=item['author'],
                    created=item['created'],
                    type=('Issue' if item in project['issues']
                          else 'PullRequest'),
                    url=item['url']))
        with open(export_path, 'w') as issues_file:
            json.dump(result, issues_file)


def main():
    handler = Handler()
    handler.export_json()
    handler.export_html()

if __name__ == '__main__':
    main()
