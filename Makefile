PYTHON_VERSION = python2.7
VIRTUALENV = virtualenv
VENV := $(shell echo $${VIRTUAL_ENV-.venv-$(PYTHON_VERSION)})
PYTHON = $(VENV)/bin/python
DEV_STAMP = $(VENV)/.dev_env_installed.stamp
INSTALL_STAMP = $(VENV)/.install.stamp
TEMPDIR := $(shell mktemp -d)
ADDONS_SERVER = https://addons.mozilla.org/
KINTO_SERVER = http://localhost:8888/v1

FIREFOX_APP_ID = "{ec8030f7-c20a-464f-9b0e-13a3a9e97384}"
THUNDERBIRD_APPID = "{3550f703-e582-4d05-9a08-453d09bdfdc6}"
SEAMONKEY_APPID = "{92650c4d-4b8e-4d2a-b7eb-24ecf4f6b63a}"
ANDROID_APPID = "{aa3c5121-dab2-40e2-81ca-7ea25febc110}"


BLOCKLIST_ARGS = "blocklist/3/$(FIREFOX_APP_ID)/45.0/"

BLOCKLIST_FILE_URL = "https://blocklist.addons.mozilla.org/$(BLOCKLIST_ARGS)"

AMO_BLOCKLIST_UI_SCHEMA = "https://raw.githubusercontent.com/mozilla-services/amo-blocklist-ui/master/amo-blocklist.json"

BLOCKLIST_BUCKET = "staging"

.IGNORE: clean distclean maintainer-clean
.PHONY: all install install-dev virtualenv tests

all: install
install: $(INSTALL_STAMP)
$(INSTALL_STAMP): $(PYTHON) setup.py
	$(VENV)/bin/pip install -Ue .
	touch $(INSTALL_STAMP)

install-dev: $(INSTALL_STAMP) $(DEV_STAMP)
$(DEV_STAMP): $(PYTHON) dev-requirements.txt
	$(VENV)/bin/pip install -r dev-requirements.txt
	touch $(DEV_STAMP)

virtualenv: $(PYTHON)
$(PYTHON):
	$(VIRTUALENV) --python /usr/bin/$(PYTHON_VERSION) $(VENV)
	$(VENV)/bin/pip install -U pip

build-requirements:
	$(VIRTUALENV) $(TEMPDIR)
	$(TEMPDIR)/bin/pip install -Ue .
	$(TEMPDIR)/bin/pip freeze > requirements.txt

tests-once: install-dev
	$(VENV)/bin/py.test --cov-report term-missing --cov-fail-under 100 --cov amo2kinto amo2kinto

tests:
	@rm -fr .coverage
	$(VENV)/bin/tox

functional: install-dev need-kinto-running
	$(VENV)/bin/tox -e functional

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -type d | xargs rm -fr

distclean: clean
	rm -fr *.egg *.egg-info/ dist/ build/

maintainer-clean: distclean
	rm -fr .venv* .tox/

sync: install
	$(VENV)/bin/json2kinto --server $(KINTO_SERVER) --addons-server $(ADDONS_SERVER) \
        --certificates-bucket $(BLOCKLIST_BUCKET) --addons-bucket $(BLOCKLIST_BUCKET) \
        --plugins-bucket $(BLOCKLIST_BUCKET) --gfx-bucket $(BLOCKLIST_BUCKET)

blocklist.xml: update-blocklist-file
update-blocklist-file:
	wget -O blocklist.xml $(BLOCKLIST_FILE_URL)

generated-blocklist.xml: sync generate-blocklist-file
generate-blocklist-file:
	$(VENV)/bin/kinto2xml -s http://localhost:8888/v1 -o generated-blocklist.xml

verify-blocklists:
	$(VENV)/bin/xml-verifier blocklist.xml generated-blocklist.xml

update-schemas:
	wget -O schemas.json $(AMO_BLOCKLIST_UI_SCHEMA)

install-kinto: $(VENV)/bin/kinto
$(VENV)/bin/kinto: install
	$(VENV)/bin/pip install kinto

run-kinto: $(VENV)/bin/kinto
	$(VENV)/bin/kinto --ini config/kinto.ini start

need-kinto-running:
	@curl http://localhost:8888/v1 2>/dev/null 1>&2 || (echo "Run 'make run-kinto' before starting tests." && exit 1)

verify-server: sync
	$(VENV)/bin/xml-verifier $(AMO_SERVER)/$(BLOCKLIST_ARGS) $(KINTO_SERVER)/$(BLOCKLIST_ARGS)
