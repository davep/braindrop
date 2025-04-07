app    := braindrop
src    := src/
tests  := tests/
run    := rye run
test   := rye test
python := $(run) python
lint   := rye lint -- --select I
fmt    := rye fmt
mypy   := $(run) mypy
spell  := $(run) codespell

##############################################################################
# Local "interactive testing" of the code.
.PHONY: run
run:				# Run the code in a testing context
	$(run) $(app)

.PHONY: debug
debug:				# Run the code with Textual devtools enabled
	TEXTUAL=devtools make

.PHONY: console
console:			# Run the textual console
	$(run) textual console

.PHONY: api
api:				# Explore the API with Posting
	posting --collection .posting --env .env

##############################################################################
# Setup/update packages the system requires.
.PHONY: setup
setup:				# Set up the repository for development
	rye sync
	$(run) pre-commit install

.PHONY: update
update:				# Update all dependencies
	rye sync --update-all

.PHONY: resetup
resetup: realclean		# Recreate the virtual environment from scratch
	make setup

##############################################################################
# Checking/testing/linting/etc.
.PHONY: lint
lint:				# Check the code for linting issues
	$(lint) $(src) $(tests)

.PHONY: codestyle
codestyle:			# Is the code formatted correctly?
	$(fmt) --check $(src) $(tests)

.PHONY: typecheck
typecheck:			# Perform static type checks with mypy
	$(mypy) --scripts-are-modules $(src) $(tests)

.PHONY: stricttypecheck
stricttypecheck:	        # Perform a strict static type checks with mypy
	$(mypy) --scripts-are-modules --strict $(src) $(tests)

.PHONY: test
test:				# Run the unit tests
	$(test) -v

.PHONY: spellcheck
spellcheck:			# Spell check the code
	$(spell) *.md $(src) $(tests)

.PHONY: checkall
checkall: spellcheck codestyle lint stricttypecheck test # Check all the things

##############################################################################
# Package/publish.
.PHONY: package
package:			# Package the library
	rye build

.PHONY: spackage
spackage:			# Create a source package for the library
	rye build --sdist

.PHONY: testdist
testdist: package			# Perform a test distribution
	rye publish --yes --skip-existing --repository testpypi --repository-url https://test.pypi.org/legacy/

.PHONY: dist
dist: package			# Upload to pypi
	rye publish --yes --skip-existing

##############################################################################
# Utility.
.PHONY: repl
repl:				# Start a Python REPL in the venv.
	$(python)

.PHONY: delint
delint:			# Fix linting issues.
	$(lint) --fix  $(src) $(tests)

.PHONY: pep8ify
pep8ify:			# Reformat the code to be as PEP8 as possible.
	$(fmt) $(src) $(tests)

.PHONY: tidy
tidy: delint pep8ify		# Tidy up the code, fixing lint and format issues.

.PHONY: clean
clean:				# Clean the build directories
	rm -rf dist

.PHONY: realclean
realclean: clean		# Clean the venv and build directories
	rm -rf .venv

.PHONY: help
help:				# Display this help
	@grep -Eh "^[a-z]+:.+# " $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.+# "}; {printf "%-20s %s\n", $$1, $$2}'

##############################################################################
# Housekeeping tasks.
.PHONY: housekeeping
housekeeping:			# Perform some git housekeeping
	git fsck
	git gc --aggressive
	git remote update --prune

### Makefile ends here
