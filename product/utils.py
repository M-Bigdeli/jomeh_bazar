from django.conf import settings
from django.urls import reverse


def update_products_list_navbar():
    from .models import Category
    def get_category_html(category):
        category_html = ""
        if category.children.all():
            category_html += '<li class="nav-item">\n<a href="' + str(reverse(
                'product:products') + category.slug + '/') + '" class="nav-link">\n' + category.name + '\n<i class="bx bx-chevron-down"></i>\n</a>\n<ul class="dropdown-menu">\n'
            for j in category.children.all():
                category_html += get_category_html(j) + ""
            category_html += "</ul>\n</li>\n"
        else:
            category_html += '<li class="nav-item">' + '\n<a href="' + str(reverse(
                'product:products') + category.slug + '/') + '" class="nav-link">' + '\n' + category.name + '\n</a>' + '\n</li>\n'
        return category_html

    primary_categories = Category.objects.filter(parent=None)
    categories_html = ""
    for primary_category in primary_categories:
        categories_html += get_category_html(primary_category)
    html_file = open((str(settings.TEMPLATES[0]["DIRS"][0]) + '\\product\\products_list_navbar.html'), 'w',
                     encoding="utf-8")
    html_file.write(categories_html)
    html_file.close()
