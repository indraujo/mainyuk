from django.db import models
from decimal import Decimal
from django.db.models import Sum


class Player(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    @property
    def total_paid(self):
        return self.gameplayer_set.aggregate(total=Sum("paid_amount"))[
            "total"
        ] or Decimal("0.00")

    @property
    def total_share(self):
        return self.gameplayer_set.aggregate(total=Sum("share_amount"))[
            "total"
        ] or Decimal("0.00")

    @property
    def balance(self):
        return self.total_paid - self.total_share

    def __str__(self):
        return self.name


class GameSession(models.Model):
    date = models.DateField()
    location = models.CharField(max_length=100)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_auto_split = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_paid(self):
        return sum((gp.paid_amount for gp in self.players.all()), Decimal("0.00"))

    @property
    def total_outstanding(self):
        return self.total_cost - self.total_paid

    @property
    def payment_completion_percent(self):
        if self.total_cost == 0:
            return 0
        return round((self.total_paid / self.total_cost) * 100, 2)

    def __str__(self):
        return f"{self.location} - {self.date}"

    def split_cost_equally(self):
        players = self.players.all()
        count = players.count()

        if count == 0:
            return

        share = (self.total_cost / count).quantize(Decimal("0.01"))

        for gp in players:
            gp.share_amount = share
            gp.save()


class GamePlayer(models.Model):
    game_session = models.ForeignKey(
        "GameSession", on_delete=models.CASCADE, related_name="players"
    )
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    share_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def outstanding_amount(self):
        if self.share_amount is None:
            return Decimal("0.00")
        return self.share_amount - self.paid_amount

    @property
    def payment_status(self):
        if not self.share_amount or self.share_amount == 0:
            return "UNPAID"

        if self.paid_amount <= 0:
            return "UNPAID"
        elif self.paid_amount < self.share_amount:
            return "PARTIAL"
        else:
            return "PAID"

    def save_model(self, request, obj, form, change):
        if "share_amount" in form.changed_data:
            obj.game_session.is_auto_split = False
            obj.game_session.save(update_fields=["is_auto_split"])
        super().save_model(request, obj, form, change)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        game = self.game_session

        if not game.is_auto_split:
            return

        players = game.players.all()
        count = players.count()

        if count == 0:
            return

        split_amount = game.total_cost / count

        for gp in players:
            if gp.share_amount is None:
                gp.share_amount = split_amount
                super(GamePlayer, gp).save(update_fields=["share_amount"])

    def __str__(self):
        # return f"{self.player.name} - {self.game_session}"
        return f"{self.player.name}"
