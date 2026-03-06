"""
公共配置：从环境变量读取认证信息
"""

import os
import sys


class Settings:
    base_url: str = "https://ai.coreshub.cn"
    access_key: str = os.getenv("QY_ACCESS_KEY_ID", "")
    secret_key: str = os.getenv("QY_SECRET_ACCESS_KEY", "")
    user_id: str = os.getenv("CORESHUB_USER_ID", "")

    def validate(self) -> None:
        """检查必填配置是否存在，缺失时打印提示并退出"""
        missing = []
        if not self.access_key:
            missing.append("QY_ACCESS_KEY_ID")
        if not self.secret_key:
            missing.append("QY_SECRET_ACCESS_KEY")
        if not self.user_id:
            missing.append("CORESHUB_USER_ID")
        if missing:
            print(
                f"[错误] 缺少必要的环境变量：{', '.join(missing)}\n"
                "请先执行：\n"
                "  export QY_ACCESS_KEY_ID=<your-ak>\n"
                "  export QY_SECRET_ACCESS_KEY=<your-sk>\n"
                "  export CORESHUB_USER_ID=<your-user-id>",
                file=sys.stderr,
            )
            sys.exit(1)


settings = Settings()
