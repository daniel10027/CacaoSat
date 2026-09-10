from __future__ import annotations

from marshmallow import EXCLUDE, Schema, fields, validate

MAX_PER_PAGE = 200


class PaginationArgs(Schema):
    class Meta:
        unknown = EXCLUDE  # les filtres (q, bbox, cooperative_id, …) sont lus à part

    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Integer(load_default=25, validate=validate.Range(min=1, max=MAX_PER_PAGE))
    sort = fields.String(load_default=None)
    order = fields.String(load_default="asc", validate=validate.OneOf(["asc", "desc"]))


def paginated(items: list, page: int, per_page: int, total: int) -> dict:
    pages = (total + per_page - 1) // per_page if per_page else 1
    return {
        "items": items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1,
        },
    }


pagination_args = PaginationArgs()
