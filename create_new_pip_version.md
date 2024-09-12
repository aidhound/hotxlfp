Send new version to pip

# Make sure tests pass

python setup.py test

# Update supported formulas

python -m "scripts.update_supported_formulas"

# Edit

setup.py - bump the version and download url
changelog.md - put the change you made there

# Create the release in github

push everything to master

Go to
https://github.com/aidhound/hotxlfp/releases

Press draft a new release

# Upload to pypi

delete stuff inside dist/*

python setup.py sdist bdist_wheel

twine upload dist/*