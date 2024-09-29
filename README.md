# purpose

This is a template for new django projects -- to standardize on some nice features/practices, and to get up and running, locally, easily and quickly. It provides instructions for getting the code from GitHub, installing it, setting up a virtual environment, and lists a few things to try after getting the webapp running. Finally, it lists the nice features/practices.

--- 


# local-install

Notes about the install instructions...

- The install-instructions below assume a unix-like environment (ie Mac, Linux, or Windows Subsystem for Linux (WSL)). 
- The install-instructions below reference `x_project_stuff`, `x_project`, and `x_app`. In all cases replace with the name of your project, like: `isbn_api_project_stuff`, `isbn_api_project`, and `isbn_api_app`.
- You'll also need to update, in the install-instructions, the path to the version of python you're using. Sensible suggestion: use the version of python used by the oldest server on which you'll be running the code. (Django 4.2x requires at least Python 3.8.)
- The `update_project_and_app_references.py` script ([link](https://github.com/Brown-University-Library/django_template_42_project/blob/main/update_project_and_app_references.py)) deletes the cloned `.git` directory (in addition to its main purpose to rename the project). Why? So you don't accidentally start building away and commit to the template repo. After this installation, creating a new git repo is one of the first things you should do.
- When you run the `pip istall ...` command, you may get a message about upgrading pip, with instructions. That's always a good idea, but not necessary for this install.
- When you start the webapp via `runserver`, you'll get a message that there are migrations that need to be run, with instructions. You can go ahead and do that, or do it later (this is a one-time thing).

```bash
## setup directories
$ mkdir ./x_project_stuff
$ cd ./x_project_stuff/
$ mkdir ./logs
$ mkdir ./DBs

## get the project-code
$ git clone https://github.com/Brown-University-Library/django_template_42_project.git

## update project-name (line below is a single long line; clarifying in case it wraps)
$ /path/to/python3 ./django_template_42_project/update_project_and_app_references.py --target_dir "./django_template_42_project/" --new_project_name "x_project" --new_app_name "x_app"  

## setup the envar-settings
$ cd ./x_project/
$ cp ./config/dotenv_example_file.txt ../.env

## setup the virtual-environment
$ /path/to/python3 -m venv ../venv
$ source ../venv/bin/activate
(venv) $ pip install pip-tools
(venv) $ pip-compile ./config/requirements/requirements_base.in
(venv) $ pip install -r ./config/requirements/requirements_base.txt
(venv) $ python ./manage.py runserver
```

That's it!

---

# stuff to try

- Open a browser to <http://127.0.0.1:8000/>. That'll redirect to <http://127.0.0.1:8000/info/>. 

- Try adding `?format=json` to the info url to see the data feeding the the template.

- Try <http://127.0.0.1:8000/error_check/>. You'll see the intentionally-raised error in the browser (would result in a `404` on production), but if you want to confirm that this really would send an email, open another terminal window and type:
    ```bash
    $ python3 -m smtpd -n -c DebuggingServer localhost:1026
    ```

    You won't initially see anything, but if you reload the error-check url, and then check this terminal window again, you'll see the email-data that would have been sent.

- Try <http://127.0.0.1:8000/version/>. Once you `git init`, `git add --all`, and `git commit -am "initial commit"`, it'll show the branch and commit -- super-handy for dev and prod confirmations.

- Try `(venv) $ python ./manage.py test`. There are two simple tests that should pass. (Requires venv to be sourced.)

- Check out the logs (`project_stuff/logs/`). The envar log-level is `DEBUG`, easily changed. On the servers that should be `INFO` or higher, and remember to rotate them, not via python's log-rotate -- but by the server's log-rotate.

Next -- well, the sky's the limit!

---


# nice features/practices

- Nothing private is in the project-repo; avoids using the `.gitignore` for security.
- Shows pattern to keep `views.py` functions short-ish, to act as manager functions (eg `views.version()`).
- Shows pattern to expose the data used by the page via adding `?format=json` (eg `views.info()`). Useful for developing the front-end and troubleshooting.
- Log-formatting shows useful stuff.
- Git branch/commit url is constructed in a way that avoids the new git `dubious ownership` error.
- Includes a couple of client-get tests that respond differentially to dev and prod settings.
- Includes a dev-only error-check url (enables confirmation that email-admins-on-error is set up correctly).
- Uses python-dotenv.
- Uses tilde-comparators in the `.in` requirements files for stable upgrades.
- Uses layered `base.in` and `server.in` requirements files which will produce `.txt` files -- for clarity re what's really in the venv. 
- Specifies compatible package versions for reliable staging and prod deployment.
- Shows one possible pattern to make async calls (`app/lib/version_helper.manage_git_calls()`) and gather together the results.
- This webapp doesn't access the db much, but if it did, and you wanted to inspect the sql generated by the ORM, uncomment out the `django.db.backends` logger in `settings.py`.

---
