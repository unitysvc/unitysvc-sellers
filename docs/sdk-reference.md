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

### SecretsResource

::: unitysvc_sellers.resources.secrets.SecretsResource
    options:
      members:
        - list
        - get
        - create
        - rotate
        - delete

### ServicesResource

::: unitysvc_sellers.resources.services.ServicesResource
    options:
      show_root_heading: true

### PromotionsResource

::: unitysvc_sellers.resources.promotions.PromotionsResource
    options:
      show_root_heading: true

### GroupsResource

::: unitysvc_sellers.resources.groups.GroupsResource
    options:
      show_root_heading: true

### DocumentsResource

::: unitysvc_sellers.resources.documents.DocumentsResource
    options:
      show_root_heading: true

### TasksResource

::: unitysvc_sellers.resources.tasks.TasksResource
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
