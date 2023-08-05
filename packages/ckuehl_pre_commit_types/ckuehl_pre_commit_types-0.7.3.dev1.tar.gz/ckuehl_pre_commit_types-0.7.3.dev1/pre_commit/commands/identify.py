from pre_commit import git
from pre_commit.file_classifier.classifier import classify


def identify(args):
    path = args.path
    # TODO: check if in the git repo first
    print(classify(path, git.guess_git_type_for_file(path)))
