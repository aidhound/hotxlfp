Send new version to pip

# Make sure tests pass

uv run python -m unittest discover

# Update supported formulas

uv run python -m "scripts.update_supported_formulas"

# Edit

pyproject.toml - bump the version and download url
changelog.md - put the changes you made there

# Create the release in github

push everything to master

Go to
https://github.com/aidhound/hotxlfp/releases

Press draft a new release

# Upload to pypi

delete stuff inside dist/*

uv build

twine upload dist/*
