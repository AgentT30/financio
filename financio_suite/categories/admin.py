from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model"""
    
    list_display = [
        'name', 
        'type', 
        'get_parent_name', 
        'user', 
        'is_default', 
        'is_active',
        'color_preview',
        'get_depth_display',
        'created_at'
    ]
    list_filter = ['type', 'is_default', 'is_active', 'created_at']
    search_fields = ['name', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'get_full_path']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'type', 'parent')
        }),
        ('Display Settings', {
            'fields': ('color', 'is_default', 'is_active')
        }),
        ('Hierarchy', {
            'fields': ('get_full_path',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_parent_name(self, obj):
        """Display parent category name"""
        return obj.parent.name if obj.parent else '-'
    get_parent_name.short_description = 'Parent'
    
    def color_preview(self, obj):
        """Display color preview in admin"""
        if obj.color:
            return f'<span style="display:inline-block;width:20px;height:20px;background-color:{obj.color};border:1px solid #ccc;"></span> {obj.color}'
        return '-'
    color_preview.short_description = 'Color'
    color_preview.allow_tags = True
    
    def get_depth_display(self, obj):
        """Display hierarchy depth"""
        return f"Level {obj.get_depth()}"
    get_depth_display.short_description = 'Depth'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'parent')
    
    class Media:
        css = {
            'all': ('admin/css/category_admin.css',)
        }
