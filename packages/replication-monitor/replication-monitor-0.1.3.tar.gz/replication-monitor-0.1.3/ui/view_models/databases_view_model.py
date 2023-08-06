from gi.repository import Gdk

from src.gtk_helper import GtkHelper
from src.listview_model import ListViewModel

from ui.listview_models.databases_listview_model import DatabasesListViewModel


class DatabasesViewModel:
    DRAG_BUTTON_MASK = Gdk.ModifierType.BUTTON1_MASK
    DRAG_TARGETS = [('text/plain', 0, 0)]
    DRAG_ACTION = Gdk.DragAction.COPY

    def __init__(self, listview, drag_and_drop=True):
        self._listview = listview
        self._model = DatabasesListViewModel()
        self._sorted_model = ListViewModel.Sorted(self._model)
        self._listview.set_model(self._sorted_model)

        # enable drag and drop
        if drag_and_drop:
            self._listview.enable_model_drag_source(self.DRAG_BUTTON_MASK, self.DRAG_TARGETS, self.DRAG_ACTION)
            self._listview.enable_model_drag_dest(self.DRAG_TARGETS, self.DRAG_ACTION)

    @property
    @GtkHelper.invoke_func_sync
    def selected(self):
        selected = []
        (_, path_list) = self._listview.get_selection().get_selected_rows()
        if path_list and len(path_list):
            for path in path_list:
                db = self._model[path]
                selected.append(db)
        return selected

    @GtkHelper.invoke_func
    def append(self, db):
        self._model.append(db)

    @GtkHelper.invoke_func
    def remove(self, db_name):
        for index, db in enumerate(self._model.rows):
            if db_name == db.db_name:
                itr = self._model.get_iter(index)
                self._model.remove(itr)

    @GtkHelper.invoke_func
    def update(self, databases):
        old_databases = {}
        new_databases = []

        itr = self._model.get_iter_first()
        while itr is not None:
            db = self._model[itr]
            old_databases[db.db_name] = self._model.get_path(itr)
            itr = self._model.iter_next(itr)

        for db in databases:
            i = old_databases.pop(db.db_name, None)
            if i is not None:
                self._model[i] = db
            else:
                new_databases.append(db)

        deleted_database_paths = [path for path in old_databases.values()]
        for path in reversed(deleted_database_paths):
            itr = self._model.get_iter(path)
            self._model.remove(itr)

        for db in new_databases:
            self._model.append(db)

    @GtkHelper.invoke_func
    def clear(self):
        self._model.clear()
