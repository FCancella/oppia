# coding: utf-8
#
# Copyright 2014 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Services for managing subscriptions."""

from __future__ import annotations

from core.platform import models
from core.domain.user_domain import UserSubscriptions

from typing import List, Optional

MYPY = False
if MYPY: # pragma: no cover
    from mypy_imports import user_models

(user_models,) = models.Registry.import_models([models.Names.USER])


def subscribe_to_thread(user_id: str, feedback_thread_id: str) -> None:
    """Subscribes a user to a feedback thread.

    WARNING: Callers of this function should ensure that the user_id and
    feedback_thread_id are valid.

    Args:
        user_id: str. The user ID of the new subscriber.
        feedback_thread_id: str. The ID of the feedback thread.
    """
    subscribe_to_threads(user_id, [feedback_thread_id])


def subscribe_to_threads(user_id: str, feedback_thread_ids: List[str]) -> None:
    """Subscribes a user to feedback threads.

    WARNING: Callers of this function should ensure that the user_id and
    the feedback_thread_ids are valid.

    Args:
        user_id: str. The user ID of the new subscriber.
        feedback_thread_ids: list(str). The IDs of the feedback threads.
    """
    user_subscriptions = get_user_subscriptions(user_id)
    if user_subscriptions is None:
        user_subscriptions = UserSubscriptions.create_default(user_id)

    # Using sets for efficiency.
    current_feedback_thread_ids_set = set(
        user_subscriptions.general_feedback_thread_ids
    )
    # Determine which thread_ids are not already in the subscriptions.
    feedback_thread_ids_to_add = list(
        set(feedback_thread_ids).difference(current_feedback_thread_ids_set)
    )
    user_subscriptions.general_feedback_thread_ids.extend(
        feedback_thread_ids_to_add
    )
    save_user_subscriptions(user_subscriptions)


def subscribe_to_exploration(user_id: str, exploration_id: str) -> None:
    """Subscribes a user to an exploration (and, therefore, indirectly to all
    feedback threads for that exploration).

    WARNING: Callers of this function should ensure that the user_id and
    exploration_id are valid.

    Args:
        user_id: str. The user ID of the new subscriber.
        exploration_id: str. The exploration ID.
    """
    user_subscriptions = get_user_subscriptions(user_id)
    if user_subscriptions is None:
        user_subscriptions = UserSubscriptions.create_default(user_id)

    if exploration_id not in user_subscriptions.exploration_ids:
        user_subscriptions.exploration_ids.append(exploration_id)
        save_user_subscriptions(user_subscriptions)


def subscribe_to_creator(user_id: str, creator_id: str) -> None:
    """Subscribes a user (learner) to a creator.

    WARNING: Callers of this function should ensure that the user_id and
    creator_id are valid.

    Args:
        user_id: str. The user ID of the new subscriber.
        creator_id: str. The user ID of the creator.

    Raises:
        Exception. The user ID of the new subscriber is same as the
            user ID of the creator.
    """
    if user_id == creator_id:
        raise Exception('User %s is not allowed to self subscribe.' % user_id)
    subscribers_model_creator = user_models.UserSubscribersModel.get(
        creator_id, strict=False)
    user_subscriptions = get_user_subscriptions(user_id)

    if not subscribers_model_creator:
        subscribers_model_creator = user_models.UserSubscribersModel(
            id=creator_id)

    if user_subscriptions is None:
        user_subscriptions = UserSubscriptions.create_default(user_id)

    if user_id not in subscribers_model_creator.subscriber_ids:
        subscribers_model_creator.subscriber_ids.append(user_id)
        user_subscriptions.creator_ids.append(creator_id)
        subscribers_model_creator.update_timestamps()
        subscribers_model_creator.put()
        save_user_subscriptions(user_subscriptions)


def unsubscribe_from_creator(user_id: str, creator_id: str) -> None:
    """Unsubscribe a user from a creator.

    WARNING: Callers of this function should ensure that the user_id and
    creator_id are valid.

    Args:
        user_id: str. The user ID of the subscriber.
        creator_id: str. The user ID of the creator.
    """
    subscribers_model_creator = user_models.UserSubscribersModel.get(
        creator_id)
    user_subscriptions = get_user_subscriptions(user_id)

    if user_id in subscribers_model_creator.subscriber_ids:
        subscribers_model_creator.subscriber_ids.remove(user_id)
        user_subscriptions.creator_ids.remove(creator_id)
        subscribers_model_creator.update_timestamps()
        subscribers_model_creator.put()
        save_user_subscriptions(user_subscriptions)


def get_all_threads_subscribed_to(user_id: str) -> List[str]:
    """Returns a list with ids of all the feedback and suggestion threads to
    which the user is subscribed.

    WARNING: Callers of this function should ensure that the user_id is valid.

    Args:
        user_id: str. The user ID of the subscriber.

    Returns:
        list(str). IDs of all the feedback and suggestion threads to
        which the user is subscribed.
    """
    user_subscriptions = get_user_subscriptions(user_id)
    if user_subscriptions:
        return user_subscriptions.general_feedback_thread_ids
    else:
        return []


def get_all_creators_subscribed_to(user_id: str) -> List[str]:
    """Returns a list with ids of all the creators to which this learner has
    subscribed.

    WARNING: Callers of this function should ensure that the user_id is valid.

    Args:
        user_id: str. The user ID of the subscriber.

    Returns:
        list(str). IDs of all the creators to which this learner has
        subscribed.
    """
    user_subscriptions = get_user_subscriptions(user_id)
    if user_subscriptions:
        return user_subscriptions.creator_ids
    else:
        return []


def get_all_subscribers_of_creator(user_id: str) -> List[str]:
    """Returns a list with ids of all users who have subscribed to this
    creator.

    WARNING: Callers of this function should ensure that the user_id is valid.

    Args:
        user_id: str. The user ID of the subscriber.

    Returns:
        list(str). IDs of all users who have subscribed to this creator.
    """
    subscribers_model = user_models.UserSubscribersModel.get(
        user_id, strict=False)
    # TODO(#15621): The explicit declaration of type for ndb properties should
    # be removed. Currently, these ndb properties are annotated with Any return
    # type. Once we have proper return type we can remove this.
    if subscribers_model:
        subscriber_ids: List[str] = subscribers_model.subscriber_ids
        return subscriber_ids
    else:
        return []


def get_exploration_ids_subscribed_to(user_id: str) -> List[str]:
    """Returns a list with ids of all explorations that the given user
    subscribes to.

    WARNING: Callers of this function should ensure that the user_id is valid.

    Args:
        user_id: str. The user ID of the subscriber.

    Returns:
        list(str). IDs of all explorations that the given user
        subscribes to.
    """
    user_subscriptions = get_user_subscriptions(user_id)
    if user_subscriptions:
        return user_subscriptions.exploration_ids
    else:
        return []


def subscribe_to_collection(user_id: str, collection_id: str) -> None:
    """Subscribes a user to a collection.

    WARNING: Callers of this function should ensure that the user_id and
    collection_id are valid.

    Args:
        user_id: str. The user ID of the new subscriber.
        collection_id: str. The collection ID.
    """
    user_subscriptions = get_user_subscriptions(user_id)
    if user_subscriptions is None:
        user_subscriptions = UserSubscriptions.create_default(user_id)

    if collection_id not in user_subscriptions.collection_ids:
        user_subscriptions.collection_ids.append(collection_id)
        save_user_subscriptions(user_subscriptions)


def get_collection_ids_subscribed_to(user_id: str) -> List[str]:
    """Returns a list with ids of all collections that the given user
    subscribes to.

    WARNING: Callers of this function should ensure that the user_id is valid.

    Args:
        user_id: str. The user ID of the subscriber.

    Returns:
        list(str). IDs of all collections that the given user
        subscribes to.
    """
    user_subscriptions = get_user_subscriptions(user_id)
    if user_subscriptions:
        return user_subscriptions.collection_ids
    else:
        return []


def get_user_subscriptions(user_id: str) -> Optional[UserSubscriptions]:
    """Returns the UserSubscriptions domain object for the given user."""

    model = user_models.UserSubscriptionsModel.get(user_id, strict=False)
    if model is None:
        return None
    return UserSubscriptions(
        id=model.id,
        creator_ids=model.creator_ids,
        collection_ids=model.collection_ids,
        activity_ids=model.activity_ids,
        general_feedback_thread_ids=model.general_feedback_thread_ids,
        exploration_ids=model.exploration_ids,
        last_checked=model.last_checked
    )


def save_user_subscriptions(user_subscriptions: UserSubscriptions) -> None:
    """Saves the UserSubscriptions domain object to storage."""

    model = user_models.UserSubscriptionsModel.get(user_subscriptions.id, strict=False)
    if model is None:
        model = user_models.UserSubscriptionsModel(id=user_subscriptions.id)

    model.creator_ids = user_subscriptions.creator_ids
    model.collection_ids = user_subscriptions.collection_ids
    model.activity_ids = user_subscriptions.activity_ids
    model.general_feedback_thread_ids = user_subscriptions.general_feedback_thread_ids
    model.exploration_ids = user_subscriptions.exploration_ids
    model.last_checked = user_subscriptions.last_checked
    model.update_timestamps()
    model.put()
