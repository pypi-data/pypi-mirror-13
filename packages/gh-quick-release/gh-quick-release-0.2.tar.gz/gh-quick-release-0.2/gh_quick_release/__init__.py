

import os
from argparse import ArgumentParser
import simplejson as json

from .GitClient import GitClient
from .GhClient import GhClient

# Increments the patch version.
def increment_version(version):
    first_dot = version.find('.')
    major = version[0 : first_dot]
    second_dot = version.find('.', first_dot + 1)
    minor = version[first_dot + 1 : second_dot]
    # If the patch number doesn't exist, default to 1.
    patch = version[second_dot + 1 : len(version)]
    if patch == '':
        return major + '.' + minor + '.' + '1'
    else:
        patch_number = int(patch) + 1
        return major + '.' + minor + '.' + str(patch_number)

# Info needed:
# - Commit message for the version bump.
# - The version that the release will be made for.
# - The branch that we will merge into.
# - The branch that we will merge from.
# - The release title
# - The release description
# - Is it a pre-release?
# Returns a dict with the information passed by the user along with sensible
# defaults of applied.
def get_args(package):
    parser = ArgumentParser()
    parser.add_argument(
        '--commit-msg',
        '-c',
        dest='commit',
        help='The commit message that will be used when pushing the changes to the package.json',
    )
    parser.add_argument(
        '--version',
        '-v',
        help='The version you want to bump this to (by default it will increment the patch number)'
    )
    parser.add_argument(
        '--from-branch',
        '-f',
        help='The branch you want to merge from',
        default='develop'
    )
    parser.add_argument(
        '--into-branch',
        '-i',
        help='The branch you will merge into',
        default='master'
    )
    parser.add_argument(
        '--release-title',
        '-t',
        help='The release title! (defaults to "Release version $version")'
    )
    parser.add_argument(
        '--release-description',
        '-d',
        default='',
        help='The release description (defaults to blank)'
    )
    parser.add_argument(
        '--pre-release',
        '-p',
        default=True,
        type=bool,
        help='Should be release be flagged as pre-release on Github?'
    )
    parser.add_argument(
        '--indent',
        '-n',
        default='\t',
        help='The indentation style to use when outputing the package.json file'
    )
    parser.add_argument(
        '--remote',
        '-r',
        default='origin',
        help='The remote to push the changes to (defaults to origin)'
    )
    parser.add_argument(
        '--verbose',
        '-b',
        type=bool,
        default=True,
        help='Spits out information about what is going on (defaults to true)'
    )
    parser.add_argument(
        '--cmd-redirect',
        '-e',
        type=bool,
        default=True,
        help='Tells the utility to redirect the git messages to /dev/null'
    )

    args = parser.parse_args()
    # Some additional defaults need to be generated from the information
    # specified by the user.
    if args.version == None:
        args.version = increment_version(package['version'])

    if args.commit == None:
        args.commit = 'Update package.json for release v' + args.version

    if args.release_title == None:
        args.release_title = 'Release v' + args.version

    return args

package_path = os.getcwd() + '/package.json'

def load_package_json():
    with open(package_path) as file:
        return json.loads(file.read())

def write_package_json(package, args):
    txt = json.dumps(package, indent=args.indent)
    with open(package_path, 'w') as file:
        file.write(txt)

def publish_change(say, git, args):
    git_output = git.check_output('rev-parse', '--abbrev-ref', 'HEAD')
    current_branch = git_output.replace('\n', '')
    if current_branch != args.from_branch:
        msg = """
        Need to be on the {0} branch. Currently on the {1} branch.
        """.format(args.from_branch, current_branch)
        raise CliError(msg)
    git.add('package.json')
    git.commit('-m', args.commit)
    say('Commited changes')
    git.checkout(args.into_branch)
    git.merge(args.from_branch, '--no-edit')
    say('Merged into branch ' + args.into_branch)
    git.push(args.remote, args.from_branch)
    git.push(args.remote, args.into_branch)
    say('Pushed to remote updates')
    # return to the original branch
    git.checkout(args.from_branch)

def create_release(say, git, args):
    # First start by extracting the owner and repo from the remote
    remote_conf = git.check_output('remote', 'show', args.remote)
    remote_url = remote_conf.split('\n')[2]
    remote_end = remote_url[remote_url.rfind(':') + 1 : len(remote_url)]
    remote_parts = remote_end.split('/')

    owner = remote_parts[0]
    repo_part = remote_parts[1]
    repo = repo_part[0 : len(repo_part) - 4]
    say('Owner is: ' + owner)
    say('Repo is: ' + repo)

    # And now I can send my payload :D
    user = os.getenv('GH_USER')
    pw = os.getenv('GH_PASSWORD')
    if user == None:
        msg = '''
        Github username must be specified through the environment variable
        GH_USER
        '''
        raise CliError(msg)
    if pw == None:
        msg = '''
        Github password must be specified through the environment variable
        GH_PASSWORD
        '''
        raise CliError(msg)
    client = GhClient(os.getenv('GH_USER'), os.getenv('GH_PASSWORD'))

    payload = {
        'tag_name': 'v' + args.version,
        'target_commitish': args.into_branch,
        'name': args.release_title,
        'body': args.release_description,
        'prerelease': args.pre_release
    }
    return client.post('repos/' + owner + '/' + repo + '/releases', payload)
    
def main():
    try:
        package = load_package_json()
        args = get_args(package)
        package['version'] = args.version

        def say(msg):
            if args.verbose == True:
                print(msg)
        git = GitClient(args.cmd_redirect)

        write_package_json(package, args)
        say('Wrote to file package.json version update')
        publish_change(say, git, args)
        create_release(say, git, args)
        say('Release created')
    except CliError, err:
        print(err.msg)

#main()

