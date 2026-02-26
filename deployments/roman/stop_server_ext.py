import os
import asyncio
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.utils import url_path_join
from tornado.web import authenticated
from tornado.httpclient import AsyncHTTPClient, HTTPRequest


# Tell Jupyter Server that this module contains an extension
def _jupyter_server_extension_points():
    return [{"module": "stop_server_ext"}]

def _load_jupyter_server_extension(server_app):
    web_app = server_app.web_app
    base_url = web_app.settings.get("base_url", "/")

    route = url_path_join(base_url, "stopme")
    web_app.add_handlers(".*", [(route, StopMeHandler)])

    server_app.log.info("[stop_server_ext] Loaded. Route: %s", route)


class StopMeHandler(JupyterHandler):
    @authenticated
    async def get(self):

        # 1) Send redirect right away so the browser leaves the dying /user/... page

        # 2) Schedule the Hub DELETE slightly later to ensure response is flushed
        user  = os.environ.get("JUPYTERHUB_USER")
        api   = os.environ.get("JUPYTERHUB_API_URL")     # e.g., http://hub:8081/hub/api
        token = os.environ.get("JUPYTERHUB_API_TOKEN")   # per-user token

        if not (user and api and token):
            # We already redirected, but log if still alive
            try:
                self.log.warning("Missing JupyterHub env (USER/API/TOKEN)")
            except Exception:
                pass
            return


        async def _stop_async():
            # small delay so the 302 response flushes to the browser first
            await asyncio.sleep(0.3)
            try:
                client = AsyncHTTPClient()
                req = HTTPRequest(
                    url=f"{api}/users/{user}/server",
                    method="DELETE",
                    headers={"Authorization": f"token {token}"},
                    request_timeout=5.0,
                    follow_redirects=False,
                )
                # We don’t raise on non-2xx; the pod may already be terminating
                await client.fetch(req, raise_error=False)
            except Exception as e:
                try:
                    self.log.warning("Async stop failed: %s", e)
                except Exception:
                    pass

        # 3) Schedule the coroutine on the current asyncio event loop
        asyncio.create_task(_stop_async())