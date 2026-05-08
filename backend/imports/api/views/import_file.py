from ninja import Router, File
from ninja.files import UploadedFile
from ninja.errors import HttpError
from imports.api.schemas.import_file import MappingDefinition
from imports.services import process_file_import
import logging
from administration.api.dependencies.auth import FullAccessAuth

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

import_file_router = Router(tags=["File Imports"])


@import_file_router.post("/create", auth=FullAccessAuth())
def import_file(
    request,
    payload: MappingDefinition,
    import_file: UploadedFile = File(...),
):
    """
    The function `import_file` uploads an import file and its mapping definition.

    Args:
        request (HttpRequest): The HTTP request object.
        payload (MappingDefinition): the mapping definition for the import
        import_file (File): the import file to upload in csv format

    Returns:
        id: the created file import id
    """
    try:
        file_import_id = process_file_import(import_file, payload)
        task_logger.info(f"File import ID #{file_import_id} started")
        return {"id": file_import_id}
    except Exception as e:
        task_logger.error("File import failed")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "File import error")
