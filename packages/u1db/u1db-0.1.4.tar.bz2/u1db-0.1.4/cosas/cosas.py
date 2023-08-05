# Copyright 2012 Canonical Ltd.
#
# This file is part of u1db.
#
# u1db is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation.
#
# u1db is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with u1db.  If not, see <http://www.gnu.org/licenses/>.

"""cosas example application."""

import os
import re
import u1db
import copy

from dirspec.basedir import save_data_path


TAGS_INDEX = 'tags'
DONE_INDEX = 'done'
INDEXES = {
    TAGS_INDEX: ['tags'],
    DONE_INDEX: ['bool(done)'],
}

TAGS = re.compile('#(\w+)|\[(.+)\]')

EMPTY_TASK = {"title": "", "done": False, "tags": []}

get_empty_task = lambda: copy.deepcopy(EMPTY_TASK)


def get_database():
    """Get the path that the database is stored in."""
    # setting document_factory to Task means that any database method that
    # would return documents, now returns Tasks instead.
    return u1db.open(
        os.path.join(save_data_path("cosas"), "cosas.u1db"), create=True,
        document_factory=Task)


def extract_tags(text):
    """Extract the tags from the text."""
    # This looks for all "tags" in a text, indicated with a '#' at the
    # start of the tag, or enclosed in square brackets.
    return [t[0] if t[0] else t[1] for t in TAGS.findall(text)]


class TodoStore(object):
    """The todo application backend."""

    def __init__(self, db):
        self.db = db

    def initialize_db(self):
        """Initialize the database."""
        # Ask the database for currently existing indexes.
        db_indexes = dict(self.db.list_indexes())
        # Loop through the indexes we expect to find.
        for name, expression in INDEXES.items():
            if name not in db_indexes:
                # The index does not yet exist.
                self.db.create_index(name, *expression)
                continue
            if expression == db_indexes[name]:
                # The index exists and is up to date.
                continue
            # The index exists but the definition is not what expected, so we
            # delete it and add the proper index expression.
            self.db.delete_index(name)
            self.db.create_index(name, *expression)

    def tag_task(self, task, tags):
        """Set the tags of a task."""
        task.tags = tags

    def get_all_tags(self):
        """Get all tags in use in the entire database."""
        return [key[0] for key in self.db.get_index_keys(TAGS_INDEX)]

    def get_tasks_by_tags(self, tags):
        """Get all tasks that have every tag in tags."""
        if not tags:
            # No tags specified, so return all tasks.
            return self.get_all_tasks()
        # Get all tasks for the first tag.
        results = dict(
            (doc.doc_id, doc) for doc in
            self.db.get_from_index(TAGS_INDEX, tags[0]))
        # Now loop over the rest of the tags (if any) and remove from the
        # results any document that does not have that particular tag.
        for tag in tags[1:]:
            # Get the ids of all documents with this tag.
            ids = [
                doc.doc_id for doc in self.db.get_from_index(TAGS_INDEX, tag)]
            for key in results.keys():
                if key not in ids:
                    # Remove the document from result, because it does not have
                    # this particular tag.
                    del results[key]
                    if not results:
                        # If results is empty, we're done: there are no
                        # documents with all tags.
                        return []
        return results.values()

    def get_task(self, doc_id):
        """Get a task from the database."""
        task = self.db.get_doc(doc_id)
        if task is None:
            # No document with that id exists in the database.
            raise KeyError("No task with id '%s'." % (doc_id,))
        if task.is_tombstone():
            # The document id exists, but the document's content was previously
            # deleted.
            raise KeyError("Task with id %s was deleted." % (doc_id,))
        return task

    def delete_task(self, task):
        """Delete a task from the database."""
        self.db.delete_doc(task)

    def new_task(self, title=None, tags=None):
        """Create a new task document."""
        if tags is None:
            tags = []
        # We make a fresh copy of a pristine task with no title.
        content = get_empty_task()
        # If we were passed a title or tags, or both, we set them in the object
        # before storing it in the database.
        if title or tags:
            content['title'] = title
            content['tags'] = tags
        # Store the document in the database. Since we did not set a document
        # id, the database will store it as a new document, and generate
        # a valid id.
        return self.db.create_doc(content)

    def save_task(self, task):
        """Save task to the database."""
        # Get the u1db document from the task object, and save it to the
        # database.
        self.db.put_doc(task)

    def get_all_tasks(self):
        # Since the DONE_INDEX indexes anything that has a value in the field
        # "done", and all tasks do (either True or False), it's a good way to
        # get all tasks out of the database.
        return self.db.get_from_index(DONE_INDEX, "*")


class Task(u1db.Document):
    """A todo item."""

    def _get_title(self):
        """Get the task title."""
        return self.content.get('title')

    def _set_title(self, title):
        """Set the task title."""
        self.content['title'] = title

    title = property(_get_title, _set_title, doc="Title of the task.")

    def _get_done(self):
        """Get the status of the task."""
        return self.content.get('done', False)

    def _set_done(self, value):
        """Set the done status."""
        self.content['done'] = value

    done = property(_get_done, _set_done, doc="Done flag.")

    def _get_tags(self):
        """Get tags associated with the task."""
        return self.content.setdefault('tags', [])

    def _set_tags(self, tags):
        """Set tags associated with the task."""
        self.content['tags'] = list(set(tags))

    tags = property(_get_tags, _set_tags, doc="Task tags.")
