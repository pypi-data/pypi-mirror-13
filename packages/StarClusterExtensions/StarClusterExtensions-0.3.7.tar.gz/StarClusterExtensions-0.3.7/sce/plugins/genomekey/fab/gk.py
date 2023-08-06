from fabric.contrib import files

from fabric.decorators import task
from fabric.operations import local
from fabric.state import env
from fabric.api import run, hide, cd, settings
import os
from sce.plugins.genomekey.util import tobool
from sce.plugins.genomekey.fab import VE


__author__ = 'erik'


@task
def copy_genomekey_dev_environ(user='genomekey', reinstall=True):
    reinstall = tobool(reinstall)
    with settings(user=user), hide('output'):

        if reinstall:
            run('rm -rf ~/projects/GenomeKey')

        if not (os.path.exists(os.path.expanduser('GenomeKey')) and os.path.exists(os.path.expanduser('Cosmos'))):
            raise AssertionError, "'WARNING! ~/projects/GenomeKey' and '~/projects/Cosmos' do not exist, cannot do setup"
        else:
            run('mkdir -p ~/projects')

            # Sync Files.  Note, assumes GenomeKey and Cosmos are installed in the CWD
            local('rsync -avP -e "ssh -o StrictHostKeyChecking=no -i {0}" GenomeKey {1}@{2}:~/projects'.format(
                env.key_filename[0], env.user, env.host))
            local('rsync -avP -e "ssh -o StrictHostKeyChecking=no -i {0}" Cosmos {1}@{2}:~/projects'.format(
                env.key_filename[0], env.user, env.host))

            # Upload our .genomekey.conf if one isnt already on server
            # if not files.exists('~/.genomekey.conf'):
            #     run('mkdir -p ~/.genomekey')
            #     files.upload_template('genomekey.conf',
            #                           '~/.genomekey/genomekey.conf', template_dir='~/.genomekey')

            # Create VirtualEnv, and install GenomeKey
            with cd('~/projects/GenomeKey'):
                if not files.exists('ve'):
                    run('pip install virtualenv --user')
                    run('virtualenv ve')
                    with VE():
                        run('pip install .')
                        run('pip install pygraphviz')
                        run('pip uninstall genomekey -y')
                        run('pwd >> ve/lib/python2.7/site-packages/includes.pth')

                        with cd('~/projects/Cosmos'):
                            run('pip uninstall cosmos-wfm -y')
                            run('pwd >> ~/projects/GenomeKey/ve/lib/python2.7/site-packages/includes.pth')


                        if not files.exists('~/bin/genomekey'):
                            run('mkdir -p ~/bin')
                            run('ln -s ~/projects/GenomeKey/bin/genomekey ~/bin/genomekey')

                        # run('~/bin/genomekey initdb')