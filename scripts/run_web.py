"""入口：启动 Web 服务。

用法：
    python scripts/run_web.py            # 默认 8000 端口
    uvicorn hiresignal.web.app:app --reload
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn  # noqa: E402


def main():
    uvicorn.run("hiresignal.web.app:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
