# unitysvc-sellers

Seller-facing tools for [UnitySVC](https://unitysvc.com/). This package
currently provides the `usvc_seller` CLI for **local** seller catalog
organization — no network calls, no UnitySVC API interactions.

The catalog HTTP SDK (`unitysvc_sellers.client`, upload, publish, etc.)
is not yet implemented; see the roadmap below.

## Install

```bash
pip install unitysvc-sellers
```

This pulls in [`unitysvc-core`](https://pypi.org/project/unitysvc-core/)
for the shared data models, JSON schemas, and generic file validator,
plus `typer`/`rich` for the CLI.

## CLI: `usvc_seller`

```
usvc_seller data validate [DATA_DIR]           # schema + catalog-layout validation
usvc_seller data format   [DATA_DIR]           # normalize JSON/TOML/MD files
usvc_seller data populate [DATA_DIR]           # run provider populate scripts
usvc_seller data show     provider  NAME       # show a provider record
usvc_seller data show     offering  NAME       #   "   offering
usvc_seller data show     listing   NAME       #   "   listing
usvc_seller data show     service   NAME       #   "   service-definition
usvc_seller data list     providers [DATA_DIR] # list files of each kind
usvc_seller data list     sellers   [DATA_DIR]
usvc_seller data list     offerings [DATA_DIR]
usvc_seller data list     listings  [DATA_DIR]
usvc_seller data list     services  [DATA_DIR]
usvc_seller data list-tests                    # list code-example / connectivity tests
usvc_seller data run-tests                     # run tests locally
usvc_seller data show-test SERVICE             # show last test result
```

All commands operate on the seller's local catalog directory. No
`usvc_seller data upload` yet — that arrives with the HTTP SDK.

## Layout

```
src/unitysvc_sellers/
├── cli.py           # entry point — registers data subcommands
├── data.py          # `usvc_seller data *` command group
├── validator.py     # seller DataValidator (subclass of unitysvc_core.validator.DataValidator)
├── format_data.py   # `usvc_seller data format`
├── populate.py      # `usvc_seller data populate`
├── example.py       # `list-tests` / `run-tests` / `show-test`
├── list.py          # `usvc_seller data list *`
├── output.py        # shared Rich output helpers
└── utils.py         # seller-only helpers (resolve_provider_name,
                     #  resolve_service_name_for_listing,
                     #  convert_convenience_fields_to_documents,
                     #  render_template_file, execute_script_content,
                     #  determine_interpreter)
                     # Generic helpers re-exported from unitysvc_core.utils.
```

The seller `DataValidator` adds catalog-layout checks to the core
per-file validator: provider-status warnings, the invariant that each
service directory has exactly one `offering_v1` file, and the invariant
that listings only live alongside an offering.

## History

This package was split out of
[`unitysvc-services`](https://github.com/unitysvc/unitysvc-services)
(see [issue #99](https://github.com/unitysvc/unitysvc-services/issues/99)).
Shared types + schemas moved to
[`unitysvc-core`](https://github.com/unitysvc/unitysvc-core); seller CLI
and seller-specific catalog utilities live here.

## Roadmap

- `unitysvc_sellers.client` / `AsyncClient` — HTTP SDK against
  `/sellers/*` endpoints
- `usvc_seller data upload` — thin Typer wrapper over
  `client.upload(...)`
- `unitysvc_sellers.builders` — catalog-builder helpers
  (`populate_from_iterator`, `render_template_file`, etc.) for
  `unitysvc-services-*` data repositories

## License

MIT
