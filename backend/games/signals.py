from decimal import Decimal
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import GameSession, GamePlayer

def split_cost(game):
    if not game.is_auto_split:
        return

    players = game.players.all()
    count = players.count()

    if count == 0:
        return

    share = (game.total_cost / count).quantize(Decimal("0.01"))

    for gp in players:
        if gp.share_amount is None:
            gp.share_amount = share
            gp.save(update_fields=["share_amount"])
            
@receiver(post_save, sender=GameSession)
def split_on_game_save(sender, instance, **kwargs):
    split_cost(instance)

@receiver(post_save, sender=GamePlayer)
@receiver(post_delete, sender=GamePlayer)
def split_on_player_change(sender, instance, **kwargs):
    split_cost(instance.game_session)
