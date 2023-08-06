from oscar.core.loading import get_model, get_class
from telegrambot.bot_views import generic
from telegrambot.models import AuthToken

Category = get_model('catalogue', 'Category')
Product = get_model('catalogue', 'Product')
Order = get_model('order', 'Order')
Selector = get_class('partner.strategy', 'Selector')

class StartView(generic.TemplateCommandView):
    template_text = "oscar_telegrambot/messages/command_start_text.txt"
    
class HelpView(generic.TemplateCommandView):
    template_text = "oscar_telegrambot/messages/command_help_text.txt"
    
class UnknownView(generic.TemplateCommandView):
    template_text = "oscar_telegrambot/messages/command_unknown_text.txt"
    
class CategoryListView(generic.ListCommandView):
    template_text = "oscar_telegrambot/messages/command_categories_list_text.txt"
    template_keyboard = "oscar_telegrambot/messages/command_categories_list_keyboard.txt"
    model = Category
    context_object_name = "category_list"
    
class CategoryDetailView(generic.DetailCommandView):
    template_text = "oscar_telegrambot/messages/command_categories_detail_text.txt"
    template_keyboard = "oscar_telegrambot/messages/command_categories_detail_keyboard.txt"
    context_object_name = "product_list"
    
    def __init__(self, slug=None):
        super(CategoryDetailView, self).__init__(slug)
        self.category = Category.objects.get(slug=self.get_slug())
        
    def get_queryset(self):
        qs = Product.browsable.base_queryset()
        if self.slug:
            qs = qs.filter(categories__in=self.category.get_descendants_and_self
                           ()).distinct()
        return qs
    
    def get_context(self, bot, update):
        products = self.get_queryset().all()        
        context = {'context_object_name': products}
        if self.context_object_name:
            context[self.context_object_name] = products
        context['category'] = self.category
        selector = Selector()
        context['request'] = selector.strategy()
        return context
        
    
class CategoryListDetailView(generic.ListDetailCommandView):
    list_view_class = CategoryListView
    detail_view_class = CategoryDetailView
    
    
class ProductDetailView(generic.DetailCommandView):
    template_text = "oscar_telegrambot/messages/command_products_detail_text.txt"
    context_object_name = "product"
    model = Product
    slug_field = 'slug'
    
class ProductSelectOneView(generic.ListCommandView):
    template_text = "oscar_telegrambot/messages/command_products_list_text.txt"
    template_keyboard = "oscar_telegrambot/messages/command_products_list_keyboard.txt"
    model = Category
    context_object_name = "category_list"
    
class ProductListDetailView(generic.ListDetailCommandView):
    list_view_class = ProductSelectOneView
    detail_view_class = ProductDetailView
    
class OrdersDetailView(generic.DetailCommandView):
    template_text = "oscar_telegrambot/messages/command_orders_detail_text.txt"
    context_object_name = "order"
    model = Order
    slug_field = 'number'
    
class OrdersListView(generic.ListCommandView):
    template_text = "oscar_telegrambot/messages/command_orders_list_text.txt"
    template_keyboard = "oscar_telegrambot/messages/command_orders_list_keyboard.txt"
    context_object_name = "order_list"
    model = Order
    
    def get_context(self, bot, update, **kwargs):
        chat_id = update.message.chat.id
        token = AuthToken.objects.get(chat_api__id=chat_id)
        orders = self.get_queryset().filter(user=token.user)     
        context = {'context_object_name': orders}
        if self.context_object_name:
            context[self.context_object_name] = orders
        return context
    
class OrdersCommandView(generic.ListDetailCommandView):
    list_view_class = OrdersListView
    detail_view_class = OrdersDetailView
