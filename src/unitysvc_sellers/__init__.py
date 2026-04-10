"""UnitySVC Sellers — seller-facing tools for UnitySVC.

This package currently provides:

- ``usvc_seller`` CLI with ``usvc_seller data *`` commands for organizing
  local seller catalogs (validate, format, populate, show, list, run test
  scripts).

Future additions (separate modules, not yet present):

- ``unitysvc_sellers.client`` / ``AsyncClient`` — seller HTTP SDK
- ``unitysvc_sellers.builders`` — catalog-builder helpers for
  ``unitysvc-services-*`` data repositories
- ``usvc_seller data upload`` — re-added when the SDK lands
"""

__author__ = """Bo Peng"""
__email__ = "bo.peng@unitysvc.com"
