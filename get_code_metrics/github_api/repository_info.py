import time
import get_code_metrics.github_api.post_query as post_query


class RepositoryInfo:
    query_repository_state = ''
    access_token = ''

    def __init__(self, token):
        self.access_token = token

    @staticmethod
    def create_repository_info_query(name_with_owner: str):
        query_state = """
        query{
          repository(owner: "%s", name: "%s") {
            nameWithOwner
            createdAt
            stargazers {
              totalCount
            }
            hasIssuesEnabled
            isArchived
            isFork
            isDisabled
            url
          }
          rateLimit {
            remaining
          }
        }
        """

        # owner, nameが存在しない場合はNoneをreturn
        if '/' in name_with_owner:
            owner = name_with_owner.split('/')[0]
            name = name_with_owner.split('/')[1]
            query_state = query_state % (owner, name)
        else:
            return None

        # queryとして送出できる形にする
        res_query = {'query': query_state}
        return res_query

    def get_repository_info(self, name_with_owner):
        # queryを作成
        query = self.create_repository_info_query(name_with_owner)
        # queryとアクセストークンを渡してpost
        repository_info = post_query.post_query(query, self.access_token)

        # repositoryが存在しないならNoneを返す
        if 'errors' in repository_info:
            print('ERRORS:', name_with_owner,
                  'doesn\'t exists or has errors. so can\'t get it.')
            return None

        # API制限回避のためrateLimitが1000以下ならsleep
        if repository_info['data']['rateLimit']['remaining'] <= 1000:
            time.sleep(3600)

        return repository_info['data']['repository']

    def get_all_repositories_info(self, repository_list):
        res_all_repository = {}

        # APIがはじめに制限にかかりそうならsleepを挟む
        post_query.avoid_api_limit(self.access_token)

        for repository in repository_list:
            repository_info = self.get_repository_info(repository)

            # 返り値がNoneなら何もしない
            if repository_info is None:
                continue
            res_all_repository.update({repository: repository_info})

        return res_all_repository
