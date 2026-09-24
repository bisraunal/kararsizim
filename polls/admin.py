from django.contrib import admin
from .models import Poll, Option, Vote

class OptionInline(admin.TabularInline):
    model = Option
    extra = 2
    min_num = 2
    max_num = 5

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'user', 'category', 'is_active', 'total_votes', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('question', 'description', 'user__username')
    inlines = [OptionInline]

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('poll', 'option', 'user', 'session_key', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('poll__question', 'option__text', 'user__username')
