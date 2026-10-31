# Rooms

A **room** is a message space on UnitySVC. As a seller you meet rooms in
three places:

- your own `me` and `helpdesk` rooms;
- rooms your service gives its customers through an enrollment;
- your customers' email, reached through their enrollment address.

This guide covers each, with the SDK and the `usvc seller rooms` CLI. For
method signatures, see the [SDK Reference](../sdk-reference.md#rooms).

## Kinds of rooms

| Kind | What it is | Owner | Messages kept |
|---|---|---|---|
| `me` | Your account's private room for notes. Webhook posts that name no room land here. | Your seller account | Up to 30 days |
| `helpdesk` | Your conversation with UnitySVC support. | Your seller account | Forever |
| `chat` | A group room that an enrollment provides to the customer. | The enrolled customer | Up to 7 days; the owner may keep less, or nothing |

Each room you're in has a **handle** (`me`, `helpdesk`, …). Anywhere a room is
expected, you can pass its id or your handle for it.

**Planned:** seller-owned rooms, a private `support` room per enrollment and
service-wide `announcement` / `discussion` rooms
([unitysvc#2830](https://github.com/unitysvc/unitysvc/issues/2830)). Until
then, upload refuses those kinds.

## Give your customers a room

A channel can ask the enrolling customer to approve a room in
`customer_access_requests`. When the enrollment activates, the platform
creates the room:

```json
{
  "upstream_access_config": {
    "free": {
      "customer_access_requests": [{
        "object": "resource:room",
        "permissions": ["create"],
        "required": true,
        "justification": "Creates your group room during enrollment",
        "options": "kind=chat&max_members=100"
      }]
    }
  }
}
```

- **What gets created:** a `chat` room owned by the customer, scoped to their enrollment, with the member cap you declare. The customer invites others with a code.
- **Lifecycle:** the room is open while the enrollment is active. Pausing or cancelling the enrollment closes it without deleting anything, and reactivating opens it again.
- **Validation:** see [Exports & Dependencies](../exports-and-dependencies.md#resource-only-apps-commons). Run `usvc seller specs validate` before uploading.

## Roles and access

| Role | Read | Post | Invite | Change settings |
|---|---|---|---|---|
| `owner` | ✓ | ✓ | up to `moderator` | ✓ |
| `moderator` | ✓ | ✓ | up to `member` | |
| `member` | ✓ | ✓ | | |
| `readonly` | ✓ | | | |

- **Your role is the one you hold now,** derived from how you were admitted. A room you can't reach isn't listed, and reading it returns 404.
- **The owner can set `status`** to `readonly` (only the owner and moderators post) or back to `active`.
- **Sellers own rooms; they don't join other accounts' rooms as guests.** A chat invitation code redeemed by a seller is refused. Room kinds decide this in their membership policy.

## Operations

All of these work the same from the SDK and the CLI:

```python
from unitysvc_sellers import Client

client = Client()  # reads UNITYSVC_SELLER_API_KEY

client.rooms.list()                                  # rooms you can reach
client.rooms.list(kind="helpdesk")
client.rooms.list(enrollment=enrollment_id)          # rooms of one enrollment
client.rooms.list(service=service_id)                # a service's own rooms

page = client.rooms.get("helpdesk")                  # room + messages, oldest first
more = client.rooms.get("helpdesk", after=page.messages.next_)

client.rooms.post("helpdesk", body="Our endpoint returns 502 since 10:00 UTC.",
                  client_message_id="incident-1031")  # safe to retry for 24 h
client.rooms.members("helpdesk")
client.rooms.update(room_id, description="**Status** updates for this service.")
client.rooms.delivery("helpdesk")
client.rooms.set_delivery("helpdesk", notify="auto", email="off")
```

```bash
usvc seller rooms list --kind helpdesk
usvc seller rooms show helpdesk --after 41
usvc seller rooms post helpdesk "Our endpoint returns 502 since 10:00 UTC." --id incident-1031
usvc seller rooms members helpdesk
usvc seller rooms set <room> --description "Status updates for this service."
usvc seller rooms delivery helpdesk --notify labs/msg-to-discord
```

- **History:** pages are ordered by message offset. Pass the previous page's `next` as `after`. A message can take a moment to appear, because history is read only up to what has been fully stored.
- **Delivery:** new messages show up in the web app's notifications. Delivery through your notify and email services is planned ([unitysvc#2807](https://github.com/unitysvc/unitysvc/issues/2807) Phase 3). The settings are stored now and apply once it ships.

## Posting from other systems

A seller key with the `api:rooms` grant can post through the room webhook:

```
POST https://unitysvc.com/rooms/<API_KEY>/<room id or handle>
{"body": "Deploy 482 finished"}
```

Without a room in the path, a leading `@handle` in the body picks the room,
and a post that matches no room lands in `me`. A key can be limited to some
rooms with the `room=` option on its `api:rooms` grant. Prefer the SDK where
you can: it sends the key in a header, not the URL.

## Email a customer through their enrollment

Every enrollment has two addresses on `svcpass.com`, so you and the customer
can email each other without exchanging real addresses:

| Address | Who writes to it | Where it arrives |
|---|---|---|
| `customer-<enrollment_id>@svcpass.com` | your account manager | the customer's mailbox, through the customer's own `/email` service |
| `seller-<enrollment_id>@svcpass.com` | the customer | your account manager's verified mailbox |

- **Replying:** each delivered message's Reply-To is the other side's address, so replies go back and forth mailbox to mailbox.
- **Conditions:**
  - the enrollment is active;
  - the customer's approved policy grants `service:email` invoke;
  - the sender is a verified person with an aligned DKIM signature.

  Each address takes up to 30 messages an hour.
- **Who pays:** mail to the customer goes out through their own `/email` service, so their account pays for it.
- **Not a room:** this email is separate from rooms; messages don't appear in any room.

**Status:** the addresses are built but are being enabled on the mail side
([unitysvc#2842](https://github.com/unitysvc/unitysvc/issues/2842)); until
then, mail to them is refused.

## Support joining a room

UnitySVC support can join a room to help. When it joins or leaves, the room
gets a visible system message, so everyone in it knows.
