SHELL := bash

bootstrap: addons ## Bootstrap environment
	[ -d "oca_web" ] || git clone https://github.com/OCA/web.git -b 18.0 --depth=1 extra-addons/oca_web
	[ -d "oca_server_tools" ] || git clone https://github.com/OCA/server-tools.git -b 18.0 --depth=1 extra-addons/oca_server_tools

odoo: ## Download Odoo 16 sources
	[ -d "odoo" ] || git clone https://github.com/odoo/odoo.git -b 18.0 --depth=1 odoo
  

build: ## Build/Rebuild containers
	docker compose down
	docker compose create

start: ## Start development environment
	docker compose start

stop: ## Stop development environment
	docker compose stop

restart: ## Restart Odoo
	docker compose restart odoo

clean: ## Remove containers and volumes
	docker compose down --volumes
	docker rmi sase-odoo

test: ## Test component
	docker compose run --rm --build odoo odoo --database=sase --init=sase -u sase --test-enable --test-tags=sase --stop-after-init --log-level=info

test-demo-data:
	docker compose run --rm --build odoo odoo --database=sase --init=iam_demo -u iam_demo --test-enable --test-tags=with_demo_data --stop-after-init --log-level=info
	
coverage:
	docker compose run --build --rm odoo /bin/bash -c "python3 -m coverage run \
	--omit=*__init__.py,*__manifest__.py,*/tests/*,carbone_sdk.py \
	--source=/mnt/extra-addons/iam_base,/mnt/extra-addons/iam_common,/mnt/extra-addons/iam_contacts,/mnt/extra-addons/iam_delib,/mnt/extra-addons/iam_indicators,/mnt/extra-addons/iam_meetings,/mnt/extra-addons/iam_projects,/mnt/extra-addons/iam_pst,/mnt/extra-addons/iam_reports,/mnt/extra-addons/iam_vision \
	 /usr/bin/odoo -i iam_vision -u iam_base,iam_contacts,iam_delib,iam_indicators,iam_meetings,iam_projects,iam_pst,iam_reports,iam_vision --test-enable --database=vision --db_host=postgres --db_user=odoo --db_password=odoo --test-tags iam --log-level=info --stop-after-init \
	&& python3 -m coverage report -m \
	&& python3 -m coverage html -d /home/coverage_html_report"

test_module: ## Test module
	docker compose run --rm odoo odoo --database=vision --init=${TEST_MODULE} --test-tags=${TEST_MODULE} --stop-after-init --log-level=info
shell: ## Start shell
	docker compose run --rm odoo odoo shell --database=vision

addons:
	mkdir addons

deep_restart: clean build start ## Full clean (containers, volumes, images) and restart

first_start: bootstrap build start  ## First start

addons != ls -d addons/*/ | grep iam
feature_environment: ## Configure git repos in order to test a feature nammed FEAT which eventually impact multiple repos. Usage : make feature_environment FEAT=PST-133
	echo "Branching git repos to $(FEAT)"
	for repo in $(addons); do \
		cd $$repo; \
		echo "Branching $$repo"; \
		git checkout $(FEAT); \
		cd -;\
	done

help: ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
