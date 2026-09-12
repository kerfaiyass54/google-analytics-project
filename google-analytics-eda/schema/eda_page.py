from pydantic import BaseModel

from schema.eda_document import EdaDocument


class EdaPage(BaseModel):

    content: list[EdaDocument]

    page: int

    size: int

    total_elements: int

    total_pages: int