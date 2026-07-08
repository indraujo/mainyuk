from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Game(models.Model):
    game_date = models.DateField()
    court_name = models.CharField(max_length=100)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.court_name} - {self.game_date}"


class GamePlayer(models.Model):
    PAYMENT_STATUS = (
        ("UNPAID", "Unpaid"),
        ("PARTIAL", "Partial"),
        ("PAID", "Paid"),
    )

    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name="participants"
    )
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="games")
    share_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS, default="UNPAID"
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("game", "player")

    def __str__(self):
        return f"{self.player.name} - {self.game.id}"


class Payment(models.Model):
    PAYMENT_METHOD = (
        ("CASH", "Cash"),
        ("TRANSFER", "Transfer"),
        ("EWALLET", "E-Wallet"),
    )

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="payments")
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD)
    paid_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.player.name} - {self.amount}"
