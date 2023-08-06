#!/usr/bin/python


MAX_VERSIONS = 50
app_id = ""

try:
    import os
    import sys
    import subprocess
    import urllib2
    import json
    import fileinput
    import datetime
    import urllib

    cwd = (os.getcwd() + "/auto_deploy")
    home = os.path.expanduser("~")

    options = []
    command = ""
    latest_branch = ""
    parameters = []


    def extract_options(s):
        for i in s:
            if i in 'abcdefghijklmnopqrstuvwxyz':
                options.append(i)


    def colorize(text, color=None):
        if color == 'red':
            return '\033[1;31m' + text + '\033[0m'
        elif color == 'blue':
            return '\033[1;34m' + text + '\033[0m'
        elif color == 'green':
            return '\033[1;32m' + text + '\033[0m'
        elif color == 'yellow':
            return '\033[1;33m' + text + '\033[0m'
        elif color == 'magenta' or color == 'pink':
            return '\033[1;35m' + text + '\033[0m'
        elif color == 'cyan':
            return '\033[1;36m' + text + '\033[0m'
        else:
            return text


    def run_git_fetch_checkout_and_rebase():
        git_response = subprocess.check_output(["git", "fetch"])
        print git_response
        git_response = ""

        git_response = subprocess.check_output(["git", "checkout", "master", "-f"])
        print git_response
        git_response = ""

        git_response = subprocess.check_output(["git", "rebase", "origin/master"])
        print git_response
        git_response = ""


    def run_git_fetch_checkout(branch="master"):
        git_response = subprocess.check_output(["git", "fetch"])
        print git_response
        git_response = ""

        git_response = subprocess.check_output(["git", "stash"])
        print git_response
        git_response = ""

        try:
            git_response = subprocess.check_output(["git", "checkout", branch, "-f"])
            print git_response

        except:
            data = {'say': "Error! Could not find " + command + "/" + branch}
            data = urllib.urlencode(data)
            u = urllib2.urlopen('http://symphbot.herokuapp.com/hubot/say', data)
            raise Exception

        git_response = ""


    def run_git_delete_branch(branch="master"):
        try:
            git_response = subprocess.check_output(["git", "checkout", "-b", "temp"])
            print git_response
            git_response = ""
        except:
            git_response = subprocess.check_output(["git", "checkout", "-f", "temp"])
            print git_response
            git_response = ""

        git_response = subprocess.check_output(["git", "branch", "-D", branch])
        print git_response
        git_response = ""


    def set_version_in_app_yaml(branch="master", force=False):
        try:
            for line in fileinput.input('app.yaml', inplace=True):
                if line.startswith("version: "):
                    if branch == 'master':
                        if force:
                            print "version: master"
                        else:
                            print "version: master" + datetime.datetime.utcnow().strftime('%Y%m%d%H%M')
                    else:
                        print "version: " + branch
                else:
                    print line,
            print 'Set version in app.yaml'
        except:
            for line in fileinput.input('app.yaml', inplace=True):
                if line.startswith("version: "):
                    if branch == 'master':
                        if force:
                            print "version: master"
                        else:
                            print "version: master" + datetime.datetime.utcnow().strftime('%Y%m%d%H%M')
                    else:
                        print "version: " + branch
                else:
                    print line,
            print 'Set version in app.yaml'


    def set_app_id_to_staging():
        try:
            for line in fileinput.input('app.yaml', inplace=True):
                if line.startswith("application: "):
                    line = line.strip()
                    line = line.replace("-staging","")
                    print line + "-staging"
                else:
                    print line,
            print 'Set application to staging in app.yaml'
        except:
            for line in fileinput.input('app.yaml', inplace=True):
                if line.startswith("application: "):
                    line = line.strip()
                    line = line.replace("-staging","")
                    print line + "-staging"
                else:
                    print line,
            print 'Set application to staging in app.yaml'


    def set_app_id_to_production():
        try:
            for line in fileinput.input('app.yaml', inplace=True):
                if line.startswith("application: "):
                    line = line.strip()
                    line = line.replace("-staging","")
                    print line
                else:
                    print line,
            print 'Set application to production in app.yaml'
        except:
            for line in fileinput.input('app.yaml', inplace=True):
                if line.startswith("application: "):
                    line = line.strip()
                    line = line.replace("-staging","")
                    print line
                else:
                    print line,
            print 'Set application to production in app.yaml'


    def get_app_id():
        try:
            lines = [line.strip() for line in open('app.yaml')]
        except:
            lines = [line.strip() for line in open('app.yaml')]
        for line in lines:
            if line.startswith("application: "):
                app_id = line.replace("application: ", "")
                return app_id


    def deploy():
        try:
            deploy_response = subprocess.check_output(["../.pyenv/2.7/google_appengine/appcfg.py", "update", ".", "--oauth2", "oauth2_credential_file=~/.appcfg_oauth2_tokens"])
            # deploy_response = subprocess.check_output(["../.pyenv/2.7/google_appengine/appcfg.py", "update", "src", "--oauth2", "oauth2_credential_file=~/.appcfg_oauth2_tokens"])
        except:
            deploy_response = subprocess.check_output(["../.pyenv/2.7/google_appengine/appcfg.py", "update", ".", "--oauth2", "oauth2_credential_file=~/.appcfg_oauth2_tokens"])


    def delete_version(v):
        v = v.strip()
        app_id = get_app_id()
        delete_version_response = subprocess.check_output(["../.pyenv/2.7/google_appengine/appcfg.py", "--oauth2", "oauth2_credential_file=~/.appcfg_oauth2_tokens", "delete_version", "-V", v, "-A", app_id])


    def get_versions():
        try:
            get_versions_response = subprocess.check_output(["../.pyenv/2.7/google_appengine/appcfg.py", "list_versions", "src", "--oauth2", "oauth2_credential_file=~/.appcfg_oauth2_tokens"])
        except:
            get_versions_response = subprocess.check_output(["../.pyenv/2.7/google_appengine/appcfg.py", "list_versions", ".", "--oauth2", "oauth2_credential_file=~/.appcfg_oauth2_tokens"])
        versions_list_str = get_versions_response.replace("default: [","").replace("]","")
        versions_list = versions_list_str.split(",")
        versions_list_new = []
        for version in versions_list:
            if version.strip().startswith('master'):
                versions_list_new.append(version.strip())

        if len(versions_list_new) > MAX_VERSIONS:
            versions_list_new.sort()
            print "Deleting second to the oldest version"
            delete_version(versions_list_new[1])


    def get_latest_branch():
        return subprocess.check_output(["git", "for-each-ref", "--count=1", "--sort=-committerdate", "refs/heads/", "--format='%(refname:short)'"])


    def set_default_version():
        try:
            set_default_version_response = subprocess.check_output(["../.pyenv/2.7/google_appengine/appcfg.py", "set_default_version", "src", "--oauth2", "oauth2_credential_file=~/.appcfg_oauth2_tokens"])
        except:
            set_default_version_response = subprocess.check_output(["../.pyenv/2.7/google_appengine/appcfg.py", "set_default_version", ".", "--oauth2", "oauth2_credential_file=~/.appcfg_oauth2_tokens"])

    print 'this is a test'

    latest_branch = get_latest_branch()
    print latest_branch

    if latest_branch.lower() == 'master':
        # Production
        try:
            run_git_delete_branch()
        except:
            print "No master branch to delete?"

        run_git_fetch_checkout()

        # update staging master
        try:
            set_app_id_to_staging()
            set_version_in_app_yaml("master", True)
            deploy()
            set_default_version()
        except:
            print "Error deploying master to staging"

        # update production
        set_app_id_to_production()
        set_version_in_app_yaml()
        get_versions()
        deploy()
        set_default_version()
    else:
        # Staging
        try:
            run_git_delete_branch(parameters[0])
        except:
            print "No branch to delete?"

        try:
            run_git_fetch_checkout(parameters[0])
            set_app_id_to_staging()
            set_version_in_app_yaml(parameters[0])
            deploy()
        except:
            print "Error deploying branch to staging"

        # Do NOT deploy to production staging anymore
        # try:
        #   set_app_id_to_production()
        #   set_version_in_app_yaml("staging")
        #   get_versions()
        #   deploy()
        # except:
        #   print "Error deploying branch to staging 2"
    # Parse args into command, options, and parameters
    # args = sys.argv
    # for arg in args[1:]:
    #     if arg.startswith("-"):
    #         extract_options(arg)

    #     elif arg == cwd:
    #         continue

    #     elif not command:
    #         command = arg

    #     else:
    #         parameters.append(arg)

    # try:
    #     os.chdir('/root/Projects/' + command)  #temp
    # except:
    #     print "Project not found."
    # else:

    #     if parameters:
    #         # staging
    #         try:
    #             run_git_delete_branch(parameters[0])
    #         except:
    #             print "No branch to delete?"

    #         try:
    #             run_git_fetch_checkout(parameters[0])
    #             set_app_id_to_staging()
    #             set_version_in_app_yaml(parameters[0])
    #             deploy()
    #         except:
    #             print "Error deploying branch to staging"

    #         # Do NOT deploy to production staging anymore
    #         # try:
    #         #   set_app_id_to_production()
    #         #   set_version_in_app_yaml("staging")
    #         #   get_versions()
    #         #   deploy()
    #         # except:
    #         #   print "Error deploying branch to staging 2"
    #     else:
    #         # production
    #         try:
    #             run_git_delete_branch()
    #         except:
    #             print "No master branch to delete?"

    #         run_git_fetch_checkout()

    #         # update staging master
    #         try:
    #             set_app_id_to_staging()
    #             set_version_in_app_yaml("master", True)
    #             deploy()
    #             set_default_version()
    #         except:
    #             print "Error deploying master to staging"

    #         # update production
    #         set_app_id_to_production()
    #         set_version_in_app_yaml()
    #         get_versions()
    #         deploy()
    #         set_default_version()



except KeyboardInterrupt:
    print "\n"
    print "Interrupted. Exiting."

