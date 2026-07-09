import argparse
import os
import sys
import time

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from ingestion.ingest import ingest_file


SUPPORTED_FORMATS = (".pdf", ".txt")


def batch_ingest(folder_path: str, skip_errors: bool = True) -> dict:
    """
    Process all supported documents from a folder and store them in ChromaDB.

    Args:
        folder_path: Path to the folder containing documents.
        skip_errors: Continue processing if an error occurs.

    Returns:
        Dictionary containing ingestion summary.
    """

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    # Find supported files
    all_files = [
        os.path.join(folder_path, file_name)
        for file_name in os.listdir(folder_path)
        if file_name.lower().endswith(SUPPORTED_FORMATS)
    ]

    if not all_files:
        print(f"No supported files found in: {folder_path}")
        print(f"Supported formats: {', '.join(SUPPORTED_FORMATS)}")

        return {
            "total": 0,
            "success": 0,
            "failed": 0,
            "total_chunks": 0,
            "time_taken": 0,
        }

    total = len(all_files)

    print("\nBatch Ingestion Started")
    print("-" * 50)
    print(f"Folder : {folder_path}")
    print(f"Files  : {total}")
    print(f"Formats: {', '.join(SUPPORTED_FORMATS)}")
    print("-" * 50)

    success = 0
    failed = 0
    total_chunks = 0
    failed_files = []

    start_time = time.time()

    for index, file_path in enumerate(all_files, start=1):

        filename = os.path.basename(file_path)

        print(f"\n[{index}/{total}] Processing: {filename}")

        try:
            result = ingest_file(file_path, verbose=False)

            success += 1
            total_chunks += result["chunks_created"]

            print(
                f"Success | "
                f"{result['chunks_created']} chunks | "
                f"{result['time_taken']} sec"
            )

        except Exception as e:

            failed += 1
            failed_files.append(filename)

            print(f"Failed : {e}")

            if not skip_errors:
                print("Batch ingestion stopped due to an error.")
                break

    elapsed = round(time.time() - start_time, 2)

    print("\n" + "-" * 50)
    print("Batch Ingestion Completed")
    print("-" * 50)
    print(f"Total Files      : {total}")
    print(f"Successfully Done: {success}")
    print(f"Failed           : {failed}")
    print(f"Total Chunks     : {total_chunks}")
    print(f"Processing Time  : {elapsed} seconds")

    if failed_files:
        print("\nFailed Files:")
        for file_name in failed_files:
            print(f" - {file_name}")

    return {
        "total": total,
        "success": success,
        "failed": failed,
        "total_chunks": total_chunks,
        "time_taken": elapsed,
    }


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Batch ingest all PDF and TXT documents into ChromaDB."
    )

    parser.add_argument(
        "folder",
        nargs="?",
        default="./my_documents",
        help="Path to the folder containing documents."
    )

    parser.add_argument(
        "--no-skip-errors",
        action="store_true",
        help="Stop processing when an error occurs."
    )

    args = parser.parse_args()

    try:
        batch_ingest(
            folder_path=args.folder,
            skip_errors=not args.no_skip_errors,
        )

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)