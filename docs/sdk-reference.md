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

### Rooms

```python
room = client.rooms.get("helpdesk")
client.rooms.post("helpdesk", body="Please help", client_message_id="support-1")
client.rooms.update(str(room.id), description="Contact **our support team** here.")
members = client.rooms.members(str(room.id))
delivery = client.rooms.delivery(str(room.id))
if delivery.can_edit:
    client.rooms.set_delivery(str(room.id), notify="auto", email="off")
```

Descriptions are owner-written Markdown. Policy fields such as `retention_seconds`,
`keep_forever` and `permanent` describe the rules actually enforced by the server.
Only owners can update settings, and singleton rooms keep their fixed rules.

::: unitysvc_sellers.rooms.Rooms
    options:
      show_root_heading: true

::: unitysvc_sellers.arooms.AsyncRooms
    options:
      show_root_heading: true

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

### Enrollments

::: unitysvc_sellers.enrollments.Enrollments
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
