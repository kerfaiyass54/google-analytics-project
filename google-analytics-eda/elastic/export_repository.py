"""
Elasticsearch repository for EDA export history.

Responsibilities:
    - Create export records
    - Retrieve export records
    - Retrieve export history
    - Retrieve exports by email
    - Retrieve latest export
    - Count exports
    - Delete export records

The repository is responsible ONLY for Elasticsearch persistence.

It does NOT:
    - generate files
    - execute EDA analysis
    - generate visualizations
"""

from __future__ import annotations

from typing import Any

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

from elastic.client import client
from elastic.indices import EDA_EXPORTS_INDEX
from schema.eda import ExportRecord


class ExportRepository:
    """
    Repository responsible for EDA export metadata
    stored in Elasticsearch.
    """

    def __init__(
        self,
        elasticsearch_client: Elasticsearch = client,
    ) -> None:

        self._client = elasticsearch_client
        self._index = EDA_EXPORTS_INDEX

    # ========================================================
    # CREATE
    # ========================================================

    def save(
        self,
        record: ExportRecord,
    ) -> ExportRecord:
        """
        Save an export record into Elasticsearch.

        Args:
            record:
                Export metadata to persist.

        Returns:
            The saved ExportRecord including its Elasticsearch ID.
        """

        self._validate_record(
            record
        )

        document = {
            "email": record.email.strip(),
            "date": record.date,
            "filename": record.filename.strip(),
        }

        response = self._client.index(
            index=self._index,
            id=record.id,
            document=document,
            refresh="wait_for",
        )

        return record.model_copy(
            update={
                "id": response["_id"],
            }
        )

    # ========================================================
    # FIND BY ID
    # ========================================================

    def find_by_id(
        self,
        export_id: str,
    ) -> ExportRecord | None:
        """
        Retrieve an export record by Elasticsearch ID.

        Args:
            export_id:
                Elasticsearch document ID.

        Returns:
            ExportRecord when found, otherwise None.
        """

        self._validate_id(
            export_id
        )

        try:

            response = self._client.get(
                index=self._index,
                id=export_id,
            )

        except NotFoundError:

            return None

        return self._to_record(
            response
        )

    # ========================================================
    # FIND ALL
    # ========================================================

    def find_all(
        self,
        page: int = 0,
        size: int = 20,
    ) -> dict[str, Any]:
        """
        Retrieve export history using pagination.

        Pagination is zero-based.

        Args:
            page:
                Page number.

            size:
                Number of records per page.

        Returns:
            Dictionary compatible with ExportPage.
        """

        page, size = self._normalize_pagination(
            page,
            size,
        )

        response = self._client.search(
            index=self._index,
            from_=page * size,
            size=size,
            track_total_hits=True,
            sort=[
                {
                    "date": {
                        "order": "desc"
                    }
                }
            ],
        )

        return self._build_page_response(
            response=response,
            page=page,
            size=size,
        )

    # ========================================================
    # FIND BY EMAIL
    # ========================================================

    def find_by_email(
        self,
        email: str,
        page: int = 0,
        size: int = 20,
    ) -> dict[str, Any]:
        """
        Retrieve export history for a specific user.

        Args:
            email:
                User email.

            page:
                Zero-based page number.

            size:
                Number of records per page.

        Returns:
            Paginated export history.
        """

        normalized_email = (
            email.strip()
        )

        if not normalized_email:

            raise ValueError(
                "Email cannot be empty."
            )

        page, size = self._normalize_pagination(
            page,
            size,
        )

        response = self._client.search(
            index=self._index,
            from_=page * size,
            size=size,
            track_total_hits=True,
            query={
                "term": {
                    "email": normalized_email
                }
            },
            sort=[
                {
                    "date": {
                        "order": "desc"
                    }
                }
            ],
        )

        return self._build_page_response(
            response=response,
            page=page,
            size=size,
        )

    # ========================================================
    # FIND LATEST
    # ========================================================

    def find_latest(
        self,
    ) -> ExportRecord | None:
        """
        Retrieve the most recently generated export.

        Returns:
            Latest ExportRecord or None when there are no exports.
        """

        response = self._client.search(
            index=self._index,
            size=1,
            track_total_hits=False,
            sort=[
                {
                    "date": {
                        "order": "desc"
                    }
                }
            ],
        )

        hits = response[
            "hits"
        ][
            "hits"
        ]

        if not hits:

            return None

        return self._hit_to_record(
            hits[0]
        )

    # ========================================================
    # COUNT
    # ========================================================

    def count(self) -> int:
        """
        Return the total number of export records.
        """

        response = self._client.count(
            index=self._index,
        )

        return int(
            response["count"]
        )

    # ========================================================
    # COUNT BY EMAIL
    # ========================================================

    def count_by_email(
        self,
        email: str,
    ) -> int:
        """
        Return the number of exports generated by a user.
        """

        normalized_email = (
            email.strip()
        )

        if not normalized_email:

            raise ValueError(
                "Email cannot be empty."
            )

        response = self._client.count(
            index=self._index,
            query={
                "term": {
                    "email": normalized_email
                }
            },
        )

        return int(
            response["count"]
        )

    # ========================================================
    # DELETE
    # ========================================================

    def delete(
        self,
        export_id: str,
    ) -> bool:
        """
        Delete an export history record.

        Important:
            This deletes ONLY the Elasticsearch metadata.

        The physical CSV/XLSX/PDF file is not deleted here.
        """

        self._validate_id(
            export_id
        )

        try:

            response = self._client.delete(
                index=self._index,
                id=export_id,
                refresh="wait_for",
            )

            return response.get(
                "result"
            ) == "deleted"

        except NotFoundError:

            return False

    # ========================================================
    # DELETE ALL
    # ========================================================

    def delete_all(self) -> int:
        """
        Delete all export history records.

        Returns:
            Number of deleted documents.
        """

        response = self._client.delete_by_query(
            index=self._index,
            query={
                "match_all": {}
            },
            refresh=True,
            conflicts="proceed",
        )

        return int(
            response.get(
                "deleted",
                0,
            )
        )

    # ========================================================
    # EXISTS
    # ========================================================

    def exists(
        self,
        export_id: str,
    ) -> bool:
        """
        Check whether an export record exists.
        """

        self._validate_id(
            export_id
        )

        return bool(
            self._client.exists(
                index=self._index,
                id=export_id,
            )
        )

    # ========================================================
    # PRIVATE — BUILD PAGE
    # ========================================================

    def _build_page_response(
        self,
        response: Any,
        page: int,
        size: int,
    ) -> dict[str, Any]:
        """
        Convert an Elasticsearch search response
        into a paginated response.
        """

        hits = response[
            "hits"
        ][
            "hits"
        ]

        content = [
            self._hit_to_record(
                hit
            )
            for hit in hits
        ]

        total = response[
            "hits"
        ][
            "total"
        ]

        if isinstance(
            total,
            dict,
        ):
            total_elements = int(
                total.get(
                    "value",
                    0,
                )
            )

        else:
            total_elements = int(
                total
            )

        total_pages = (
            (
                total_elements
                + size
                - 1
            )
            // size
            if total_elements > 0
            else 0
        )

        return {
            "content": content,
            "page": page,
            "size": size,
            "total_elements": total_elements,
            "total_pages": total_pages,
        }

    # ========================================================
    # PRIVATE — HIT TO RECORD
    # ========================================================

    @staticmethod
    def _hit_to_record(
        hit: dict[str, Any],
    ) -> ExportRecord:
        """
        Convert an Elasticsearch hit into ExportRecord.
        """

        source = hit.get(
            "_source",
            {},
        )

        return ExportRecord(
            id=hit.get(
                "_id"
            ),
            email=source.get(
                "email",
                "",
            ),
            date=source.get(
                "date"
            ),
            filename=source.get(
                "filename",
                "",
            ),
        )

    # ========================================================
    # PRIVATE — RESPONSE TO RECORD
    # ========================================================

    @staticmethod
    def _to_record(
        response: dict[str, Any],
    ) -> ExportRecord:
        """
        Convert an Elasticsearch GET response
        into ExportRecord.
        """

        source = response.get(
            "_source",
            {},
        )

        return ExportRecord(
            id=response.get(
                "_id"
            ),
            email=source.get(
                "email",
                "",
            ),
            date=source.get(
                "date"
            ),
            filename=source.get(
                "filename",
                "",
            ),
        )

    # ========================================================
    # PRIVATE — VALIDATE RECORD
    # ========================================================

    @staticmethod
    def _validate_record(
        record: ExportRecord,
    ) -> None:
        """
        Validate the minimum repository requirements.
        """

        if not record.email.strip():

            raise ValueError(
                "Email cannot be empty."
            )

        if not record.filename.strip():

            raise ValueError(
                "Filename cannot be empty."
            )

        if record.date is None:

            raise ValueError(
                "Export date cannot be null."
            )

    # ========================================================
    # PRIVATE — VALIDATE ID
    # ========================================================

    @staticmethod
    def _validate_id(
        export_id: str,
    ) -> None:
        """
        Validate Elasticsearch document ID.
        """

        if not export_id or not export_id.strip():

            raise ValueError(
                "Export ID cannot be empty."
            )

    # ========================================================
    # PRIVATE — PAGINATION
    # ========================================================

    @staticmethod
    def _normalize_pagination(
        page: int,
        size: int,
    ) -> tuple[int, int]:
        """
        Normalize pagination values.

        Limits page size to 100 to avoid unnecessarily
        large Elasticsearch queries.
        """

        normalized_page = max(
            int(page),
            0,
        )

        normalized_size = min(
            max(
                int(size),
                1,
            ),
            100,
        )

        return (
            normalized_page,
            normalized_size,
        )