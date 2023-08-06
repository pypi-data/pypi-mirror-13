#! /usr/bin/env python3
""" usage: repo-sync CONFIG

Creates a sync repo in PWD.

Environment:
    REPONAME    name of the sync repo in workdir (Default: repo-sync.git)

Configuration:
    Sync configuration in json format,defines which branch of
    "origin.url" will be mirrored to "mirror.url"

    $name.origin.ref defaults to "heads/master"
    $name.mirror.ref defaults to "heads/${name}"

Literal example for config file:
{
    "$username-repo": {
        "origin": {
            "url": "http://github.com/username/repo"
            "ref": "heads/dev"
        },
        "mirror": {
            "url": "git@internal:mirror-repo",
            "ref": "heads/github-mirror-dev"
        },
    ...
}

"""
from git import Repo
import git
from docopt import docopt
import logging
import os
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("repo-sync")

def load_config(fname):
    import json
    with open(fname) as f:
        return json.load(f)

def mirror(reponame,cfg):
    from os.path import join
    log.info("init repo at {}".format(join(os.curdir,reponame)))
    repo = Repo.init(reponame,bare=True)
    for k,v in cfg.items():
        log.info("begin sync of {}".format(k))
        oname = k
        mname = oname+'-mirror'
        ourl = v['origin']['url']
        murl = v['mirror']['url']

        # it is easier to ask for forgiveness than to ask for permission
        try: repo.delete_remote(oname)
        except git.exc.GitCommandError: pass
        try: repo.delete_remote(mname)
        except git.exc.GitCommandError: pass

        # Step 1: fetch remote_ref:local_ref
        # Step 2: push local_ref:mirror_ref
        remote_ref = "refs/" + v['origin']['ref'] if 'ref' in v['origin'] \
                else 'refs/heads/master'
        local_ref = "refs/remotes/{}/master".format(oname)
        refspec = "+{}:{}".format(remote_ref,local_ref)
        oremote = repo.create_remote(oname,url=ourl)
        log.info("fetching refspec {}".format(refspec))
        oremote.fetch(refspec=refspec)

        mremote = repo.create_remote(mname,murl)

        mirror_ref = "refs/" + v['mirror']['ref'] if 'ref' in v['mirror'] \
                else "refs/heads/{}".format(oname)

        mrefspec = "{}:{}".format(local_ref,mirror_ref)
        log.info("pushing refspec {}".format(mrefspec))
        push = mremote.push(refspec=mrefspec,force=True)
        print(push)

def main():
    args = docopt(__doc__)
    name = os.environ.get("REPONAME","repo-sync.git")
    mirror(name,load_config(args['CONFIG']))

if __name__ == "__main__":
    main()
