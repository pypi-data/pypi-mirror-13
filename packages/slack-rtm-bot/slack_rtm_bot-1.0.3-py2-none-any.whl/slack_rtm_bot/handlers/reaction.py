import itertools

from .base import MessageHandler
from .. import settings

class ReactionHandler(MessageHandler):

  TRIGGER_ANCHOR = ''
  TRIGGER_PREFIX = ''
  TRIGGERS = sorted(
      settings.EMOJI_REACTIONS.keys() + settings.MESSAGE_REACTIONS.keys())
  HELP = 'add emoji and message reactions'

  def handle_message(self, event, triggers, query):
    for trigger in triggers:
      trigger = trigger.lower()
      for reaction in self._get_reactions(settings.EMOJI_REACTIONS, trigger):
        self.client.api_call(
            'reactions.add',
            name=reaction,
            channel=event['channel'],
            timestamp=event['ts'])
    return '\n'.join(itertools.chain.from_iterable(
        self._get_reactions(settings.MESSAGE_REACTIONS, trigger)
        for trigger in triggers))

  def _get_reactions(self, reaction_defs, trigger):
    reactions = reaction_defs.get(trigger, [])
    return [reactions] if isinstance(reactions, basestring) else reactions
