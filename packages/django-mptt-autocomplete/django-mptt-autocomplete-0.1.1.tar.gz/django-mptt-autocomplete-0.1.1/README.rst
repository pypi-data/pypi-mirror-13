Django Mptt Autocomplete Widget
----------------------

django-mptt-autocomplete provides a widget using the fancytree js library to
render a forms.ChoiceField as a tree with selectable and
collapsable nodes with an autocomplete to search in existing tree.

See included project 'treewidget' as an example. Widget is used in
ModelChoiceField and allows user to select single category.


Requirements
------------

django, django-mptt, jquery, jquery-ui


Usage
-----

::

  from mptt_autocomplete.widgets import FancyTreeWidget

  categories = Category.objects.order_by('tree_id', 'lft')

  class CategoryForm(forms.Form):
      categories = forms.ModelChoiceField(
         queryset=categories,
         widget=FancyTreeWidget(queryset=categories,model=Category)
      )


In this example Category is a model registered with django-mptt.

Widget accepts **queryset** option, which expects pre-ordered queryset by
"tree_id" and "lft".

If you want to adjust tree data creation, you can define 'get_doc' method on
your model. Example:

::

  def get_doc(self, values):
    doc = {"title": name, "key": self.pk}
    if str(self.pk) in values:
        doc['select'] = True
        doc['expand'] = True
    return doc
