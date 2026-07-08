from django.contrib import admin
from .models import Player, GameSession, GamePlayer
from decimal import Decimal


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "total_paid",
        "total_share",
        "balance",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "phone")


class GamePlayerInline(admin.TabularInline):
    model = GamePlayer
    extra = 1
    readonly_fields = ('payment_status', 'outstanding_amount')
    fields = (
        'player',
        'share_amount',
        'paid_amount',
        'payment_status',
        'outstanding_amount',
    )

    def payment_status(self, obj):
        return obj.payment_status

    payment_status.short_description = 'Status'

    def outstanding_amount(self, obj):
        return obj.outstanding_amount

    outstanding_amount.short_description = 'Outstanding'




@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'location',
        'total_cost',
        'is_auto_split',
        'total_paid_display',
        'total_outstanding_display',
        'completion_display',
    )
    list_editable = ("is_auto_split",)
    date_hierarchy = 'date'
    inlines = [GamePlayerInline]

    actions = ["split_cost"]

    def split_cost(self, request, queryset):
        for game in queryset:
            game.split_cost_equally()
        self.message_user(request, "Cost split equally among players.")

    split_cost.short_description = "Split cost equally"

    def total_paid_display(self, obj):
        return obj.total_paid

    total_paid_display.short_description = 'Total Paid'

    def total_outstanding_display(self, obj):
        return obj.total_outstanding

    total_outstanding_display.short_description = 'Outstanding'

    def completion_display(self, obj):
        return f"{obj.payment_completion_percent}%"

    completion_display.short_description = 'Completion'

    readonly_fields = (
        'summary_total_paid',
        'summary_outstanding',
        'summary_completion',
    )

    fields = (
        'date',
        'location',
        'total_cost',
        'summary_total_paid',
        'summary_outstanding',
        'summary_completion',
        'is_auto_split'
    )

    def summary_total_paid(self, obj):
        return obj.total_paid

    summary_total_paid.short_description = 'Total Paid'

    def summary_outstanding(self, obj):
        return obj.total_outstanding

    summary_outstanding.short_description = 'Outstanding'

    def summary_completion(self, obj):
        return f"{obj.payment_completion_percent}%"

    summary_completion.short_description = 'Payment Completion'



@admin.register(GamePlayer)
class GamePlayerAdmin(admin.ModelAdmin):
    list_display = (
        'player',
        'game_session',
        'share_amount',
        'paid_amount',
        'payment_status_display',
        'outstanding_amount_display',
    )


    def payment_status_display(self, obj):
        return obj.payment_status

    payment_status_display.short_description = 'Status'

    def outstanding_amount_display(self, obj):
        return obj.outstanding_amount

    outstanding_amount_display.short_description = 'Outstanding'
