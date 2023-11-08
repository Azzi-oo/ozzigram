from admin_auto_filters.filters import AutocompleteFilter


class AuthorFilter(AutocompleteFilter):
    title = 'Author'
    field_name = 'author'


class PostFilter(AutocompleteFilter):
    title = 'Post'
    field_name = 'post'
