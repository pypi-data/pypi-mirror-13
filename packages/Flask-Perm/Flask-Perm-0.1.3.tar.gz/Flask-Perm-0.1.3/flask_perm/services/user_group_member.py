# -*- coding: utf-8 -*-

from sqlalchemy.exc import IntegrityError
from ..core import db
from ..models import UserGroupMember

def create(user_id, user_group_id):
    member = UserGroupMember(
        user_id=user_id,
        user_group_id=user_group_id,
    )
    db.session.add(member)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        member = UserGroupMember.query.filter_by(
            user_id=user_id,
            user_group_id=user_group_id,
        ).first()
    return member

def get(id):
    return UserGroupMember.query.get(id)

def delete(id):
    member = UserGroupMember.query.get(id)
    if member:
        db.session.delete(member)
    db.session.commit()

def get_users_by_group(user_group_id):
    rows = UserGroupMember.query.filter_by(
        user_group_id=user_group_id
    ).with_entities(
        UserGroupMember.user_id
    ).all()
    return [row.user_id for row in rows]

def get_user_groups_by_user(user_id):
    rows = UserGroupMember.query.filter_by(
        user_id=user_id
    ).with_entities(
        UserGroupMember.user_group_id
    ).all()
    return [row.user_group_id for row in rows]

def filter_user_group_members(filter_by, offset, limit, sort_field='created_at', sort_dir='desc'):
    query = UserGroupMember.query
    if filter_by:
        query = query.filter_by(**filter_by)
    field = getattr(UserGroupMember, sort_field)
    order_by = getattr(field, sort_dir.lower())()
    return query.order_by(order_by).offset(offset).limit(limit).all()

def rest(obj):
    return dict(
        id=obj.id,
        user_id=obj.user_id,
        user_group_id=obj.user_group_id,
    )
