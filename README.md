![Python](https://img.shields.io/github/pipenv/locked/python-version/kwzrd/ryan?label=Python&style=flat-square)
![Flake8 & friends](https://img.shields.io/github/workflow/status/kwzrd/ryan/Flake8%20&%20friends?label=Flake8%20%26%20friends&style=flat-square)
![Last commit](https://img.shields.io/github/last-commit/kwzrd/ryan/master?label=Last%20commit&style=flat-square)

## Ryan

Discord bot for me & my friends. This project does not aim to provide a generic utility bot. Many of the implemented features are specific to the communities that I am part of.

### Setup & Development

See [`.env.template`](.env.template) for an example of how to set a Discord API token to login with.

We use [Pipenv](https://github.com/pypa/pipenv) for dependency management. Setup is trivial:

```
pipenv sync
pipenv run ryan
```

The [`Pipfile`](Pipfile) also tracks development dependencies, i.e. a linting suite with [Flake8](https://pypi.org/project/flake8/) and a few plugins that I like. To install and run lint:

```
pipenv sync --dev
pipenv run lint
```

This runs in CI on pull requests against `master`. There is currently no testing suite.

### Contributing

If you're interested in contributing or have questions, please get in touch with me.
