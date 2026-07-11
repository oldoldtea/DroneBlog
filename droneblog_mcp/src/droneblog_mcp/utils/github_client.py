"""DroneBlog MCP Server - GitHub API Client"""

import base64

import requests

# 所有 GitHub API 请求的默认超时（秒），避免网络抖动导致工具调用无限挂起。
DEFAULT_TIMEOUT = 30
API_BASE = "https://api.github.com"


class GitHubClient:
    """GitHub API 客户端"""

    def __init__(self, token: str, username: str, timeout: int = DEFAULT_TIMEOUT):
        self.token = token
        self.username = username
        self.timeout = timeout
        # GitHub 对 classic PAT 与 fine-grained PAT 均接受 Bearer；统一使用 Bearer。
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """发送 HTTP 请求（统一注入 timeout）。"""
        kwargs.setdefault("timeout", self.timeout)
        return requests.request(method, url, headers=self.headers, **kwargs)

    def verify_token(self) -> dict:
        """验证 Token 并获取用户信息"""
        resp = self._request("GET", f"{API_BASE}/user")
        if resp.status_code == 200:
            return {"valid": True, "user": resp.json()}
        return {"valid": False, "error": f"HTTP {resp.status_code}: {resp.text}"}

    def create_repo(
        self, name: str, description: str = "", private: bool = False, auto_init: bool = True
    ) -> dict:
        """创建仓库"""
        url = f"{API_BASE}/user/repos"
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": auto_init,
        }
        resp = self._request("POST", url, json=data)
        if resp.status_code == 201:
            return {"success": True, "repo": resp.json()}
        return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text}"}

    def repo_exists(self, name: str) -> bool:
        """检查仓库是否存在"""
        url = f"{API_BASE}/repos/{self.username}/{name}"
        resp = self._request("GET", url)
        return resp.status_code == 200

    def get_repo(self, name: str) -> dict | None:
        """获取仓库信息"""
        url = f"{API_BASE}/repos/{self.username}/{name}"
        resp = self._request("GET", url)
        if resp.status_code == 200:
            return resp.json()
        return None

    def create_or_update_file(
        self, repo: str, path: str, content: str, message: str, branch: str = "main"
    ) -> dict:
        """创建或更新文件（GitHub Contents API）"""
        url = f"{API_BASE}/repos/{self.username}/{repo}/contents/{path}"

        # 先获取文件 SHA（如果存在）
        get_resp = self._request("GET", url, params={"ref": branch})
        sha = get_resp.json().get("sha") if get_resp.status_code == 200 else None

        # 创建/更新
        data = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode(),
            "branch": branch,
        }
        if sha:
            data["sha"] = sha

        resp = self._request("PUT", url, json=data)
        if resp.status_code in (200, 201):
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text}"}

    def get_file(self, repo: str, path: str, branch: str = "main") -> str | None:
        """获取文件内容"""
        url = f"{API_BASE}/repos/{self.username}/{repo}/contents/{path}"
        resp = self._request("GET", url, params={"ref": branch})
        if resp.status_code == 200:
            data = resp.json()
            if "content" in data:
                return base64.b64decode(data["content"]).decode("utf-8")
        return None

    def enable_pages(self, repo: str, branch: str = "master") -> dict:
        """启用 GitHub Pages"""
        url = f"{API_BASE}/repos/{self.username}/{repo}/pages"
        data = {"source": {"branch": branch, "path": "/"}}
        resp = self._request("POST", url, json=data)
        if resp.status_code == 201:
            return {"success": True, "data": resp.json()}
        # 可能已经启用
        if resp.status_code == 409:
            return {"success": True, "message": "Pages already enabled"}
        return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text}"}

    def create_repo_dispatch(self, repo: str, event_type: str, payload: dict) -> bool:
        """触发 repository_dispatch"""
        url = f"{API_BASE}/repos/{self.username}/{repo}/dispatches"
        data = {"event_type": event_type, "client_payload": payload}
        resp = self._request("POST", url, json=data)
        return resp.status_code == 204

    def list_repo_files(self, repo: str, path: str = "", branch: str = "main") -> list:
        """列出仓库文件"""
        url = f"{API_BASE}/repos/{self.username}/{repo}/contents/{path}"
        resp = self._request("GET", url, params={"ref": branch})
        if resp.status_code == 200:
            return resp.json()
        return []
