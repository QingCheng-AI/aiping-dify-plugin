from dify_plugin import Plugin, DifyPluginEnv
import config

plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=config.MAX_REQUEST_TIMEOUT))

if __name__ == "__main__":
    plugin.run()
