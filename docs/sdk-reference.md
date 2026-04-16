# SDK Reference (auto-generated)

This page is auto-generated from source docstrings via
[mkdocstrings](https://mkdocstrings.github.io/). For narrative
documentation with examples, see the [SDK Guide](sdk-guide.md).

## Client

::: unitysvc_sellers.Client
    options:
      members:
        - from_env
        - services
        - promotions
        - groups
        - documents
        - secrets
        - tasks
        - upload

## AsyncClient

::: unitysvc_sellers.AsyncClient
    options:
      members:
        - from_env
        - services
        - promotions
        - groups
        - documents
        - secrets
        - tasks

## Resources

### Secrets

::: unitysvc_sellers.secrets.Secrets
    options:
      members:
        - list
        - get
        - create
        - rotate
        - delete

### Services

::: unitysvc_sellers.services.Services
    options:
      show_root_heading: true

### Promotions

::: unitysvc_sellers.promotions.Promotions
    options:
      show_root_heading: true

### Groups

::: unitysvc_sellers.groups.Groups
    options:
      show_root_heading: true

### Documents

::: unitysvc_sellers.documents.Documents
    options:
      show_root_heading: true

### Tasks

::: unitysvc_sellers.tasks.Tasks
    options:
      members:
        - get
        - wait

## Exceptions

::: unitysvc_sellers.exceptions
    options:
      members:
        - SellerSDKError
        - APIError
        - AuthenticationError
        - PermissionError
        - NotFoundError
        - ValidationError
        - ConflictError
        - RateLimitError
        - ServerError
