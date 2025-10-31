from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
from astrbot.api.provider import ProviderRequest

@register("qbot_skipthinking", "IACER1", "在提示词底部插入一条 AI(assistant) 角色提示词。", "0.1.0", "https://github.com/iACER1/qbot_skipthinking")
class SkipThinkingPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config or {}

    async def initialize(self):
        """插件初始化"""
        logger.info("[qbot_skipthinking] 已加载，尾部提示词可在插件配置中编辑。")

    @filter.on_llm_request(priority=-9999)
    async def inject_tail_prompt(self, event: AstrMessageEvent, req: ProviderRequest):
        """
        在请求 LLM 前，将一条 role=assistant 的消息追加到上下文列表的最底部。
        插入位置固定为末尾，角色固定为 assistant；提示词内容可在配置中编辑。
        """
        try:
            tail = ""
            try:
                tail = (self.config.get("tail_prompt") or "").strip()
            except Exception:
                tail = ""

            if not tail:
                return

            # 确保 contexts 存在且为列表
            contexts = getattr(req, "contexts", None)
            if contexts is None:
                req.contexts = []
            elif not isinstance(contexts, list):
                try:
                    req.contexts = list(contexts)
                except Exception:
                    req.contexts = []

            # 追加一条 assistant 角色消息到末尾
            req.contexts.append({"role": "assistant", "content": tail})
        except Exception as e:
            logger.error(f"[qbot_skipthinking] 注入尾部提示词失败: {e}")

    # 保留示例指令，便于快速自测
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个 hello world 指令"""
        user_name = event.get_sender_name()
        message_str = event.message_str
        logger.info(f"[qbot_skipthinking] /helloworld by {user_name}: {message_str}")
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!")

    async def terminate(self):
        """插件被卸载/停用时调用"""
        logger.info("[qbot_skipthinking] 已卸载")
