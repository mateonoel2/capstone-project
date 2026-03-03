import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn


def main():
    print("=" * 60)
    print("Bank Statement Extraction API")
    print("=" * 60)
    print("\nStarting server...")
    print("API will be available at: http://localhost:8000")
    print("Interactive docs at: http://localhost:8000/docs")
    print("\nPress CTRL+C to stop\n")

    uvicorn.run(
        "src.application.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()

