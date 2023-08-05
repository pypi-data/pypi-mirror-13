"""
.. module:: repository
   :platform: Unix, Windows
   :synopsis: A module for examining a single git repository

.. moduleauthor:: Will McGinnis <will@pedalwrencher.com>


"""


import os
import sys
import datetime
import time
import numpy as np
import json
import logging
import tempfile
import shutil
from git import Repo, GitCommandError
from pandas import DataFrame, to_datetime

__author__ = 'willmcginnis'


class Repository(object):
    """
    The base class for a generic git repository, from which to gather statistics.  The object encapulates a single
    gitpython Repo instance.

    :param working_dir: the directory of the git repository, meaning a .git directory is in it (default None=cwd)
    :return:
    """

    def __init__(self, working_dir=None, verbose=False):
        self.verbose = verbose
        self.log = logging.getLogger('gitpandas')
        self.__delete_hook = False
        if working_dir is not None:
            if working_dir[:3] == 'git':
                if self.verbose:
                    print('cloning repository: %s into a temporary location' % (working_dir, ))

                dir_path = tempfile.mkdtemp()
                self.repo = Repo.clone_from(working_dir, dir_path)
                self.git_dir = dir_path
                self.__delete_hook = True
            else:
                self.git_dir = working_dir
                self.repo = Repo(self.git_dir)
        else:
            self.git_dir = os.getcwd()
            self.repo = Repo(self.git_dir)

        if self.verbose:
            print('Repository [%s] instantiated at directory: %s' % (self._repo_name(), self.git_dir))

    def __del__(self):
        """
        On delete, clean up any temporary repositories still hanging around

        :return:
        """
        if self.__delete_hook:
            shutil.rmtree(self.git_dir)

    def is_bare(self):
        """
        Returns a boolean for if the repo is bare or not

        :return: bool
        """

        return self.repo.bare

    def has_coverage(self):
        """
        Returns a boolean for is a parseable .coverage file can be found in the repository

        :return: bool

        """

        if os.path.exists(self.git_dir + os.sep + '.coverage'):
            try:
                with open(self.git_dir + os.sep + '.coverage', 'r') as f:
                    blob = f.read()
                    blob = blob.split('!')[2]
                    _ = json.loads(blob)
                return True
            except:
                return False
        else:
            return False

    def coverage(self):
        """
        If there is a .coverage file available, this will attempt to form a DataFrame with that information in it, which
        will contain the columns:

         * filename
         * lines_covered
         * total_lines
         * coverage

        If it can't be found or parsed, an empty DataFrame of that form will be returned.

        :return: DataFrame
        """

        if not self.has_coverage():
            return DataFrame(columns=['filename', 'lines_covered', 'total_lines', 'coverage'])

        with open(self.git_dir + os.sep + '.coverage', 'r') as f:
            blob = f.read()
            blob = blob.split('!')[2]
            cov = json.loads(blob)

        ds = []
        for filename in cov['lines'].keys():
            idx = 0
            with open(filename, 'r') as f:
                for idx, l in enumerate(f):
                    pass
            num_lines = idx + 1
            short_filename = filename.split(self.git_dir + os.sep)[1]
            ds.append([short_filename, len(cov['lines'][filename]), num_lines])

        df = DataFrame(ds, columns=['filename', 'lines_covered', 'total_lines'])
        df['coverage'] = df['lines_covered'] / df['total_lines']

        return df

    def commit_history(self, branch='master', limit=None, extensions=None, ignore_dir=None, days=None):
        """
        Returns a pandas DataFrame containing all of the commits for a given branch. Included in that DataFrame will be
        the columns:

         * date (index)
         * author
         * committer
         * message
         * lines
         * insertions
         * deletions
         * net

        :param branch: the branch to return commits for
        :param limit: (optional, default=None) a maximum number of commits to return, None for no limit
        :param extensions: (optional, default=None) a list of file extensions to return commits for
        :param ignore_dir: (optional, default=None) a list of directory names to ignore
        :param days: (optional, default=None) number of days to return, if limit is None
        :return: DataFrame
        """

        # setup the data-set of commits
        if limit is None:
            if days is None:
                ds = [[
                          x.author.name,
                          x.committer.name,
                          x.committed_date,
                          x.message,
                          self.__check_extension(x.stats.files, extensions, ignore_dir)
                      ] for x in self.repo.iter_commits(branch, max_count=sys.maxsize)]
            else:
                ds = []
                c_date = time.time()
                commits = self.repo.iter_commits(branch, max_count=sys.maxsize)
                dlim = time.time() - days * 24 * 3600
                while c_date > dlim:
                    x = commits.__next__()
                    ds.append([
                              x.author.name,
                              x.committer.name,
                              x.committed_date,
                              x.message,
                              self.__check_extension(x.stats.files, extensions, ignore_dir)
                    ])
                    c_date = x.committed_date
        else:
            ds = [[
                      x.author.name,
                      x.committer.name,
                      x.committed_date,
                      x.message,
                      self.__check_extension(x.stats.files, extensions, ignore_dir)
                  ] for x in self.repo.iter_commits(branch, max_count=limit)]

        # aggregate stats
        ds = [x[:-1] + [sum([x[-1][key]['lines'] for key in x[-1].keys()]),
                       sum([x[-1][key]['insertions'] for key in x[-1].keys()]),
                       sum([x[-1][key]['deletions'] for key in x[-1].keys()]),
                       sum([x[-1][key]['insertions'] for key in x[-1].keys()]) - sum([x[-1][key]['deletions'] for key in x[-1].keys()])
                       ] for x in ds if len(x[-1].keys()) > 0]

        # make it a pandas dataframe
        df = DataFrame(ds, columns=['author', 'committer', 'date', 'message', 'lines', 'insertions', 'deletions', 'net'])

        # format the date col and make it the index
        df['date'] = to_datetime(df['date'].map(lambda x: datetime.datetime.fromtimestamp(x)))
        df.set_index(keys=['date'], drop=True, inplace=True)

        return df

    def file_change_history(self, branch='master', limit=None, extensions=None, ignore_dir=None):
        """
        Returns a DataFrame of all file changes (via the commit history) for the specified branch.  This is similar to
        the commit history DataFrame, but is one row per file edit rather than one row per commit (which may encapsulate
        many file changes). Included in the DataFrame will be the columns:

         * date (index)
         * author
         * committer
         * message
         * filename
         * insertions
         * deletions

        :param branch: the branch to return commits for
        :param limit: (optional, default=None) a maximum number of commits to return, None for no limit
        :param extensions: (optional, default=None) a list of file extensions to return commits for
        :param ignore_dir: (optional, default=None) a list of directory names to ignore
        :return: DataFrame
        """

        # setup the dataset of commits
        if limit is None:
            ds = [[
                      x.author.name,
                      x.committer.name,
                      x.committed_date,
                      x.message,
                      self.__check_extension(x.stats.files, extensions, ignore_dir)
                  ] for x in self.repo.iter_commits(branch, max_count=sys.maxsize)]
        else:
            ds = [[
                      x.author.name,
                      x.committer.name,
                      x.committed_date,
                      x.message,
                      self.__check_extension(x.stats.files, extensions, ignore_dir)
                  ] for x in self.repo.iter_commits(branch, max_count=limit)]

        ds = [x[:-1] + [fn, x[-1][fn]['insertions'], x[-1][fn]['deletions']] for x in ds for fn in x[-1].keys() if len(x[-1].keys()) > 0]

        # make it a pandas dataframe
        df = DataFrame(ds, columns=['author', 'committer', 'date', 'message', 'filename', 'insertions', 'deletions'])

        # format the date col and make it the index
        df['date'] = to_datetime(df['date'].map(lambda x: datetime.datetime.fromtimestamp(x)))
        df.set_index(keys=['date'], drop=True, inplace=True)

        return df

    def file_change_rates(self, branch='master', limit=None, extensions=None, ignore_dir=None, coverage=False):
        """
        This function will return a DataFrame containing some basic aggregations of the file change history data, and
        optionally test coverage data from a coverage.py .coverage file.  The aim here is to identify files in the
        project which have abnormal edit rates, or the rate of changes without growing the files size.  If a file has
        a high change rate and poor test coverage, then it is a great candidate for writing more tests.

        :param branch: (optional, default=master) the branch to return commits for
        :param limit: (optional, default=None) a maximum number of commits to return, None for no limit
        :param extensions: (optional, default=None) a list of file extensions to return commits for
        :param ignore_dir: (optional, default=None) a list of directory names to ignore
        :param coverage: (optional, default=False) a bool for whether or not to attempt to join in coverage data.
        :return: DataFrame
        """

        fch = self.file_change_history(branch=branch, limit=limit, extensions=extensions, ignore_dir=ignore_dir)
        fch.reset_index(level=0, inplace=True)

        file_history = fch.groupby('filename').agg(
            {
                'insertions': [np.sum, np.max, np.mean],
                'deletions': [np.sum, np.max, np.mean],
                'message': lambda x: ','.join(['"' + str(y) + '"' for y in x]),
                'committer': lambda x: ','.join(['"' + str(y) + '"' for y in x]),
                'author': lambda x: ','.join(['"' + str(y) + '"' for y in x]),
                'date': [np.max, np.min]
            }
        )

        file_history.columns = [' '.join(col).strip() for col in file_history.columns.values]

        file_history = file_history.rename(columns={
            'message <lambda>': 'messages',
            'committer <lambda>': 'committers',
            'insertions sum': 'total_insertions',
            'insertions amax': 'max_insertions',
            'insertions mean': 'mean_insertions',
            'author <lambda>': 'authors',
            'date amax': 'max_date',
            'date amin': 'min_date',
            'deletions sum': 'total_deletions',
            'deletions amax': 'max_deletions',
            'deletions mean': 'mean_deletions'
        })

        # get some building block values for later use
        file_history['net_change'] = file_history['total_insertions'] - file_history['total_deletions']
        file_history['abs_change'] = file_history['total_insertions'] + file_history['total_deletions']
        file_history['delta_time'] = file_history['max_date'] - file_history['min_date']
        file_history['delta_days'] = file_history['delta_time'].map(lambda x: np.ceil(x.item() / (24 * 3600 * 10e9) + 0.01))

        # calculate metrics
        file_history['net_rate_of_change'] = file_history['net_change'] / file_history['delta_days']
        file_history['abs_rate_of_change'] = file_history['abs_change'] / file_history['delta_days']
        file_history['edit_rate'] = file_history['abs_rate_of_change'] - file_history['net_rate_of_change']
        file_history['unique_committers'] = file_history['committers'].map(lambda x: len(set(x.split(','))))

        # reindex
        file_history = file_history.reindex(columns=['unique_committers', 'abs_rate_of_change', 'net_rate_of_change', 'net_change', 'abs_change', 'edit_rate'])
        file_history.sort_values(by=['edit_rate'], inplace=True)

        if coverage and self.has_coverage():
            file_history = file_history.merge(self.coverage(), left_index=True, right_on='filename', how='outer')
            file_history.set_index(keys=['filename'], drop=True, inplace=True)

        return file_history

    @staticmethod
    def __check_extension(files, extensions, ignore_dir):
        """
        Internal method to filter a list of file changes by extension and ignore_dirs.

        :param files:
        :param extensions: a list of file extensions to return commits for
        :param ignore_dir: a list of directory names to ignore
        :return: dict
        """

        if extensions is None:
            return files

        if ignore_dir is None:
            ignore_dir = []
        else:
            ignore_dir = [os.sep + str(x).replace('/', '').replace('\\', '') + os.sep for x in ignore_dir]

        out = {}
        for key in files.keys():
            if key.split('.')[-1] in extensions:
                if sum([1 if x in key else 0 for x in ignore_dir]) == 0:
                    out[key] = files[key]

        return out

    def blame(self, extensions=None, ignore_dir=None, rev='HEAD', committer=True):
        """
        Returns the blame from the current HEAD of the repository as a DataFrame.  The DataFrame is grouped by committer
        name, so it will be the sum of all contributions to the repository by each committer. As with the commit history
        method, extensions and ignore_dirs parameters can be passed to exclude certain directories, or focus on certain
        file extensions. The DataFrame will have the columns:

         * committer
         * loc

        :param extensions: (optional, default=None) a list of file extensions to return commits for
        :param ignore_dir: (optional, default=None) a list of directory names to ignore
        :param rev: (optional, default=HEAD) the specific revision to blame
        :param committer: (optional, defualt=True) true if committer should be reported, false if author
        :return: DataFrame
        """

        if ignore_dir is None:
            ignore_dir = []

        blames = []
        for roots, dirs, files in os.walk(self.git_dir):
            if '.git' not in roots and sum([1 if x in roots else 0 for x in ignore_dir]) == 0:
                if extensions is not None:
                    filenames = [roots + os.sep + x for x in files if x.split('.')[-1] in extensions]
                else:
                    filenames = [roots + os.sep + x for x in files]

                for file in filenames:
                    try:
                        blames.append(self.repo.blame(rev, str(file).replace(self.git_dir + '/', '')))
                    except GitCommandError as err:
                        pass

        blames = [item for sublist in blames for item in sublist]
        if committer:
            blames = DataFrame([[x[0].committer.name, len(x[1])] for x in blames], columns=['committer', 'loc']).groupby('committer').agg({'loc': np.sum})
        else:
            blames = DataFrame([[x[0].author.name, len(x[1])] for x in blames], columns=['committer', 'loc']).groupby('committer').agg({'loc': np.sum})

        return blames

    def revs(self, branch='master', limit=None, skip=None, num_datapoints=None):
        """
        Returns a dataframe of all revision tags and their timestamps. It will have the columns:

         * date
         * rev

        :param branch: (optional, default 'master') the branch to work in
        :param limit: (optional, default None), the maximum number of revisions to return, None for no limit
        :param skip: (optional, default None), the number of revisions to skip. Ex: skip=2 returns every other revision, None for no skipping.
        :param num_datapoints: (optional, default=None) if limit and skip are none, and this isn't, then num_datapoints evenly spaced revs will be used
        :return: DataFrame

        """

        if limit is None and skip is None and num_datapoints is not None:
            limit = sum(1 for _ in self.repo.iter_commits())
            skip = int(float(limit) / num_datapoints)
        else:
            if limit is None:
                limit = sys.maxsize
            elif skip is not None:
                limit = limit * skip

        ds = [[x.committed_date, x.name_rev.split(' ')[0]] for x in self.repo.iter_commits(branch, max_count=limit)]
        df = DataFrame(ds, columns=['date', 'rev'])

        if skip is not None:
            if df.shape[0] >= skip:
                df = df.ix[range(0, df.shape[0], skip)]
                df.reset_index()
            else:
                df = df.ix[[0]]
                df.reset_index()

        return df

    def cumulative_blame(self, branch='master', extensions=None, ignore_dir=None, limit=None, skip=None, num_datapoints=None, committer=True):
        """
        Returns the blame at every revision of interest. Index is a datetime, column per committer, with number of lines
        blamed to each committer at each timestamp as data.

        :param branch: (optional, default 'master') the branch to work in
        :param limit: (optional, default None), the maximum number of revisions to return, None for no limit
        :param skip: (optional, default None), the number of revisions to skip. Ex: skip=2 returns every other revision, None for no skipping.
        :param extensions: (optional, default=None) a list of file extensions to return commits for
        :param ignore_dir: (optional, default=None) a list of directory names to ignore
        :param num_datapoints: (optional, default=None) if limit and skip are none, and this isn't, then num_datapoints evenly spaced revs will be used
        :param committer: (optional, defualt=True) true if committer should be reported, false if author
        :return: DataFrame

        """

        revs = self.revs(branch=branch, limit=limit, skip=skip, num_datapoints=num_datapoints)

        # get the commit history to stub out committers (hacky and slow)
        committers = {x.committer.name for x in self.repo.iter_commits(branch, max_count=sys.maxsize)}
        for committer in committers:
            revs[committer] = 0

        if self.verbose:
            print('Beginning processing for cumulative blame:')

        # now populate that table with some actual values
        for idx, row in revs.iterrows():
            if self.verbose:
                print('%s. [%s] getting blame for rev: %s' % (str(idx), datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), row.rev, ))

            blame = self.blame(extensions=extensions, ignore_dir=ignore_dir, rev=row.rev, committer=committer)
            for committer in committers:
                try:
                    loc = blame.loc[committer, 'loc']
                    revs.set_value(idx, committer, loc)
                except KeyError:
                    pass

        del revs['rev']

        revs['date'] = to_datetime(revs['date'].map(lambda x: datetime.datetime.fromtimestamp(x)))
        revs.set_index(keys=['date'], drop=True, inplace=True)
        revs = revs.fillna(0.0)

        # drop 0 cols
        for col in revs.columns.values:
            if col != 'col':
                if revs[col].sum() == 0:
                    del revs[col]

        # drop 0 rows
        keep_idx = []
        committers = [x for x in revs.columns.values if x != 'date']
        for idx, row in revs.iterrows():
            if sum([row[x] for x in committers]) > 0:
                keep_idx.append(idx)

        revs = revs.ix[keep_idx]

        return revs

    def branches(self):
        """
        Returns a data frame of all branches in origin.  The DataFrame will have the columns:

         * repository
         * branch

        :returns: DataFrame
        """

        branches = self.repo.branches
        df = DataFrame([x.name for x in list(branches)], columns=['branch'])
        df['repository'] = self._repo_name()

        return df

    def tags(self):
        """
        Returns a data frame of all tags in origin.  The DataFrame will have the columns:

         * repository
         * tag

        :returns: DataFrame
        """

        tags = self.repo.tags
        df = DataFrame([x.name for x in list(tags)], columns=['tag'])
        df['repository'] = self._repo_name()

        return df

    def _repo_name(self):
        """
        Returns the name of the repository, using the local directory name.

        :returns: str
        """

        reponame = self.repo.git_dir.split(os.sep)[-2]
        if reponame.strip() == '':
            return 'unknown_repo'
        return reponame

    def __str__(self):
        """
        A pretty name for the repository object.

        :returns: str
        """
        return 'git repository: %s at: %s' % (self._repo_name(), self.git_dir, )

    def __repr__(self):
        """
        A unique name for the repository object.

        :returns: str
        """
        return str(self.git_dir)

    def bus_factor(self, extensions=None, ignore_dir=None):
        """
        An experimental heuristic for truck factor of a repository calculated by the current distribution of blame in
        the repository's primary branch.  The factor is the fewest number of contributors whose contributions make up at
        least 50% of the codebase's LOC

        :param extensions: (optional, default=None) a list of file extensions to return commits for
        :param ignore_dir: (optional, default=None) a list of directory names to ignore
        :return:
        """

        blame = self.blame(extensions=extensions, ignore_dir=ignore_dir)
        blame = blame.sort_values(by=['loc'], ascending=False)

        total = blame['loc'].sum()
        cumulative = 0
        tc = 0
        for idx in range(blame.shape[0]):
            cumulative += blame.ix[idx, 'loc']
            tc += 1
            if cumulative >= total / 2:
                break

        return tc


class GitFlowRepository(Repository):
    """
    A special case where git flow is followed, so we know something about the branching scheme
    """
    def __init__(self):
        super(Repository, self).__init__()


