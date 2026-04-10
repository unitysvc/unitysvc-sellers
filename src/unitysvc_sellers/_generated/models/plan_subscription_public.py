from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.billing_interval_enum import BillingIntervalEnum
from ..models.billing_interval_enum import check_billing_interval_enum
from ..models.plan_subscription_status_enum import check_plan_subscription_status_enum
from ..models.plan_subscription_status_enum import PlanSubscriptionStatusEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.plan_subscription_public_extra_metadata_type_0 import PlanSubscriptionPublicExtraMetadataType0
  from ..models.plan_subscription_public_pending_action_metadata_type_0 import PlanSubscriptionPublicPendingActionMetadataType0
  from ..models.pricing_plan_public import PricingPlanPublic





T = TypeVar("T", bound="PlanSubscriptionPublic")



@_attrs_define
class PlanSubscriptionPublic:
    """ Public subscription information for API responses.

     """

    billing_interval: BillingIntervalEnum
    """ Billing cycle interval. """
    amount: str
    """ Total amount charged per billing interval """
    id: UUID
    customer_id: UUID
    plan_id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    quantity: int | Unset = 1
    """ Number of seats (for per-seat plans) """
    currency: str | Unset = 'USD'
    """ Currency code """
    status: PlanSubscriptionStatusEnum | Unset = UNSET
    """ Platform subscription status (Stripe-compatible).

    Note: This is separate from SubscriptionStatusEnum which is for
    ServiceEnrollment (marketplace services). """
    started_at: datetime.datetime | Unset = UNSET
    """ Subscription start date """
    cancel_at_period_end: bool | Unset = False
    """ Cancel at end of current period (deprecated, use pending_action) """
    canceled_at: datetime.datetime | None | Unset = UNSET
    """ Cancellation date """
    ended_at: datetime.datetime | None | Unset = UNSET
    """ Subscription end date """
    pending_action: None | str | Unset = UNSET
    """ Action to execute at period end: 'cancel', 'pause', or 'downgrade' """
    pending_action_metadata: None | PlanSubscriptionPublicPendingActionMetadataType0 | Unset = UNSET
    """ Details for pending action (e.g. new_plan_id, new_quantity for downgrade) """
    trial_start: datetime.datetime | None | Unset = UNSET
    """ Trial start date """
    trial_end: datetime.datetime | None | Unset = UNSET
    """ Trial end date """
    extra_metadata: None | PlanSubscriptionPublicExtraMetadataType0 | Unset = UNSET
    """ Additional metadata """
    plan: None | PricingPlanPublic | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.plan_subscription_public_extra_metadata_type_0 import PlanSubscriptionPublicExtraMetadataType0
        from ..models.plan_subscription_public_pending_action_metadata_type_0 import PlanSubscriptionPublicPendingActionMetadataType0
        from ..models.pricing_plan_public import PricingPlanPublic
        billing_interval: str = self.billing_interval

        amount = self.amount

        id = str(self.id)

        customer_id = str(self.customer_id)

        plan_id = str(self.plan_id)

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        quantity = self.quantity

        currency = self.currency

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status


        started_at: str | Unset = UNSET
        if not isinstance(self.started_at, Unset):
            started_at = self.started_at.isoformat()

        cancel_at_period_end = self.cancel_at_period_end

        canceled_at: None | str | Unset
        if isinstance(self.canceled_at, Unset):
            canceled_at = UNSET
        elif isinstance(self.canceled_at, datetime.datetime):
            canceled_at = self.canceled_at.isoformat()
        else:
            canceled_at = self.canceled_at

        ended_at: None | str | Unset
        if isinstance(self.ended_at, Unset):
            ended_at = UNSET
        elif isinstance(self.ended_at, datetime.datetime):
            ended_at = self.ended_at.isoformat()
        else:
            ended_at = self.ended_at

        pending_action: None | str | Unset
        if isinstance(self.pending_action, Unset):
            pending_action = UNSET
        else:
            pending_action = self.pending_action

        pending_action_metadata: dict[str, Any] | None | Unset
        if isinstance(self.pending_action_metadata, Unset):
            pending_action_metadata = UNSET
        elif isinstance(self.pending_action_metadata, PlanSubscriptionPublicPendingActionMetadataType0):
            pending_action_metadata = self.pending_action_metadata.to_dict()
        else:
            pending_action_metadata = self.pending_action_metadata

        trial_start: None | str | Unset
        if isinstance(self.trial_start, Unset):
            trial_start = UNSET
        elif isinstance(self.trial_start, datetime.datetime):
            trial_start = self.trial_start.isoformat()
        else:
            trial_start = self.trial_start

        trial_end: None | str | Unset
        if isinstance(self.trial_end, Unset):
            trial_end = UNSET
        elif isinstance(self.trial_end, datetime.datetime):
            trial_end = self.trial_end.isoformat()
        else:
            trial_end = self.trial_end

        extra_metadata: dict[str, Any] | None | Unset
        if isinstance(self.extra_metadata, Unset):
            extra_metadata = UNSET
        elif isinstance(self.extra_metadata, PlanSubscriptionPublicExtraMetadataType0):
            extra_metadata = self.extra_metadata.to_dict()
        else:
            extra_metadata = self.extra_metadata

        plan: dict[str, Any] | None | Unset
        if isinstance(self.plan, Unset):
            plan = UNSET
        elif isinstance(self.plan, PricingPlanPublic):
            plan = self.plan.to_dict()
        else:
            plan = self.plan


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "billing_interval": billing_interval,
            "amount": amount,
            "id": id,
            "customer_id": customer_id,
            "plan_id": plan_id,
            "created_at": created_at,
            "updated_at": updated_at,
        })
        if quantity is not UNSET:
            field_dict["quantity"] = quantity
        if currency is not UNSET:
            field_dict["currency"] = currency
        if status is not UNSET:
            field_dict["status"] = status
        if started_at is not UNSET:
            field_dict["started_at"] = started_at
        if cancel_at_period_end is not UNSET:
            field_dict["cancel_at_period_end"] = cancel_at_period_end
        if canceled_at is not UNSET:
            field_dict["canceled_at"] = canceled_at
        if ended_at is not UNSET:
            field_dict["ended_at"] = ended_at
        if pending_action is not UNSET:
            field_dict["pending_action"] = pending_action
        if pending_action_metadata is not UNSET:
            field_dict["pending_action_metadata"] = pending_action_metadata
        if trial_start is not UNSET:
            field_dict["trial_start"] = trial_start
        if trial_end is not UNSET:
            field_dict["trial_end"] = trial_end
        if extra_metadata is not UNSET:
            field_dict["extra_metadata"] = extra_metadata
        if plan is not UNSET:
            field_dict["plan"] = plan

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.plan_subscription_public_extra_metadata_type_0 import PlanSubscriptionPublicExtraMetadataType0
        from ..models.plan_subscription_public_pending_action_metadata_type_0 import PlanSubscriptionPublicPendingActionMetadataType0
        from ..models.pricing_plan_public import PricingPlanPublic
        d = dict(src_dict)
        billing_interval = check_billing_interval_enum(d.pop("billing_interval"))




        amount = d.pop("amount")

        id = UUID(d.pop("id"))




        customer_id = UUID(d.pop("customer_id"))




        plan_id = UUID(d.pop("plan_id"))




        created_at = isoparse(d.pop("created_at"))




        updated_at = isoparse(d.pop("updated_at"))




        quantity = d.pop("quantity", UNSET)

        currency = d.pop("currency", UNSET)

        _status = d.pop("status", UNSET)
        status: PlanSubscriptionStatusEnum | Unset
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = check_plan_subscription_status_enum(_status)




        _started_at = d.pop("started_at", UNSET)
        started_at: datetime.datetime | Unset
        if isinstance(_started_at,  Unset):
            started_at = UNSET
        else:
            started_at = isoparse(_started_at)




        cancel_at_period_end = d.pop("cancel_at_period_end", UNSET)

        def _parse_canceled_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                canceled_at_type_0 = isoparse(data)



                return canceled_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        canceled_at = _parse_canceled_at(d.pop("canceled_at", UNSET))


        def _parse_ended_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                ended_at_type_0 = isoparse(data)



                return ended_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        ended_at = _parse_ended_at(d.pop("ended_at", UNSET))


        def _parse_pending_action(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pending_action = _parse_pending_action(d.pop("pending_action", UNSET))


        def _parse_pending_action_metadata(data: object) -> None | PlanSubscriptionPublicPendingActionMetadataType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                pending_action_metadata_type_0 = PlanSubscriptionPublicPendingActionMetadataType0.from_dict(data)



                return pending_action_metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PlanSubscriptionPublicPendingActionMetadataType0 | Unset, data)

        pending_action_metadata = _parse_pending_action_metadata(d.pop("pending_action_metadata", UNSET))


        def _parse_trial_start(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                trial_start_type_0 = isoparse(data)



                return trial_start_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        trial_start = _parse_trial_start(d.pop("trial_start", UNSET))


        def _parse_trial_end(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                trial_end_type_0 = isoparse(data)



                return trial_end_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        trial_end = _parse_trial_end(d.pop("trial_end", UNSET))


        def _parse_extra_metadata(data: object) -> None | PlanSubscriptionPublicExtraMetadataType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                extra_metadata_type_0 = PlanSubscriptionPublicExtraMetadataType0.from_dict(data)



                return extra_metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PlanSubscriptionPublicExtraMetadataType0 | Unset, data)

        extra_metadata = _parse_extra_metadata(d.pop("extra_metadata", UNSET))


        def _parse_plan(data: object) -> None | PricingPlanPublic | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                plan_type_0 = PricingPlanPublic.from_dict(data)



                return plan_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PricingPlanPublic | Unset, data)

        plan = _parse_plan(d.pop("plan", UNSET))


        plan_subscription_public = cls(
            billing_interval=billing_interval,
            amount=amount,
            id=id,
            customer_id=customer_id,
            plan_id=plan_id,
            created_at=created_at,
            updated_at=updated_at,
            quantity=quantity,
            currency=currency,
            status=status,
            started_at=started_at,
            cancel_at_period_end=cancel_at_period_end,
            canceled_at=canceled_at,
            ended_at=ended_at,
            pending_action=pending_action,
            pending_action_metadata=pending_action_metadata,
            trial_start=trial_start,
            trial_end=trial_end,
            extra_metadata=extra_metadata,
            plan=plan,
        )

        return plan_subscription_public

