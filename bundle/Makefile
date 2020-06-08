.PHONY: executable

executable:
	pyinstaller --hidden-import='pkg_resources.py2_warn' --clean --additional-hooks-dir=. executable.py -F -n derex
	ln -sf derex dist/ddc-project
	ln -sf derex dist/ddc-services
