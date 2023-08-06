from telegrambot.generic.responses import TextResponse, KeyboardResponse
from telegram import ParseMode
import sys
import traceback

class TemplateCommandView(object):
    template_code = None    
    
    def get_context(self, update):
        return None    

    def handle(self, bot, update):
        try:
            ctx = self.get_context(update)
            text = TextResponse(self.template_code, ctx).render()
            keyboard = KeyboardResponse(self.template_code, ctx).render()        
#             logger.debug("Text:" + str(text.encode('utf-8')))
#             logger.debug("Keyboard:" + str(keyboard))
            if text:
                bot.sendMessage(chat_id=update.message.chat_id, text=text.encode('utf-8'), reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
        except:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            raise

    @classmethod
    def as_command_view(cls, **initkwargs):
        def view(bot, update):
            self = cls(**initkwargs)
            return self.handle(bot, update)
        return view