# -*- coding: utf-8 -*-
#pylint: disable=abstract-method
#
# Copyright 2014-2025 BigML
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Base class for sources' REST calls

   https://bigml.com/api/sources

"""

import sys
import os
import numbers
import time
import logging

from urllib import parse

try:
    #added to allow GAE to work
    from google.appengine.api import urlfetch
    GAE_ENABLED = True
except ImportError:
    GAE_ENABLED = False

try:
    import simplejson as json
except ImportError:
    import json

try:
    from pandas import DataFrame
    from io import StringIO
    PANDAS_READY = True
except ImportError:
    PANDAS_READY = False

from zipfile import ZipFile

import mimetypes
import requests

from requests_toolbelt import MultipartEncoder

from bigml.util import is_url, maybe_save, filter_by_extension, \
    infer_field_type
from bigml.bigmlconnection import (
    HTTP_CREATED, HTTP_BAD_REQUEST,
    HTTP_UNAUTHORIZED, HTTP_PAYMENT_REQUIRED, HTTP_NOT_FOUND,
    HTTP_TOO_MANY_REQUESTS,
    HTTP_INTERNAL_SERVER_ERROR, GAE_ENABLED, SEND_JSON)
from bigml.bigmlconnection import json_load
from bigml.api_handlers.resourcehandler import check_resource_type, \
    resource_is_ready, get_source_id, get_id
from bigml.constants import SOURCE_PATH, IMAGE_EXTENSIONS
from bigml.api_handlers.resourcehandler import ResourceHandlerMixin, LOGGER
from bigml.fields import Fields

LOG_FORMAT = '%(asctime)-15s: %(message)s'
LOGGER = logging.getLogger('BigML')
CONSOLE = logging.StreamHandler()
CONSOLE.setLevel(logging.WARNING)
LOGGER.addHandler(CONSOLE)

MAX_CHANGES = 5
MAX_RETRIES = 5

def compact_regions(regions):
    """Returns the list of regions in the compact value used for updates """

    out_regions = []
    for region in regions:
        new_region = []
        new_region.append(region.get("label"))
        new_region.append(region.get("xmin"))
        new_region.append(region.get("ymin"))
        new_region.append(region.get("xmax"))
        new_region.append(region.get("ymax"))
        out_regions.append(new_region)
    return out_regions


class SourceHandlerMixin(ResourceHandlerMixin):

    """This class is used by the BigML class as
       a mixin that provides the REST calls to sources. It should not
       be instantiated independently.

    """

    def __init__(self):
        """Initializes the SourceHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.source_url = self.url + SOURCE_PATH

    def _create_remote_source(self, url, args=None):
        """Creates a new source using a URL

        """
        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args.update({"remote": url})
        create_args = self._add_project(create_args)
        body = json.dumps(create_args)
        return self._create(self.source_url, body)

    def _create_connector_source(self, connector, args=None):
        """Creates a new source using an external connector

        """
        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args.update({"external_data": connector})
        create_args = self._add_project(create_args)
        body = json.dumps(create_args)
        return self._create(self.source_url, body)

    def _create_inline_source(self, src_obj, args=None):
        """Create source from inline data

           The src_obj data should be a list of rows stored as dict or
           list objects.
        """
        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args = self._add_project(create_args)

        # some basic validation
        if (not isinstance(src_obj, list) or (
                not all(isinstance(row, dict) for row in src_obj) and
                not all(isinstance(row, list) for row in src_obj))):
            raise TypeError(
                'ERROR: inline source must be a list of dicts or a '
                'list of lists')

        create_args.update({"data": json.dumps(src_obj)})
        body = json.dumps(create_args)
        return self._create(self.source_url, body)

    def _create_local_source(self, file_name, args=None):
        """Creates a new source using a local file.


        """
        create_args = {}
        if args is not None:
            create_args.update(args)

        for key, value in list(create_args.items()):
            if value is not None and isinstance(value, (list, dict)):
                create_args[key] = json.dumps(value)
            elif value is not None and isinstance(value, numbers.Number):
                # the multipart encoder only accepts strings and files
                create_args[key] = str(value)


        code = HTTP_INTERNAL_SERVER_ERROR
        resource_id = None
        location = None
        resource = None
        error = {
            "status": {
                "code": code,
                "message": "The resource couldn't be created"}}

        #pylint: disable=locally-disabled,consider-using-with
        try:
            if isinstance(file_name, str):
                name = os.path.basename(file_name)
                file_handler = open(file_name, "rb")
            else:
                name = 'Stdin input'
                file_handler = file_name
        except IOError:
            sys.exit("ERROR: cannot read training set")
        qs_params = self._add_credentials({})
        qs_str = "?%s" % parse.urlencode(qs_params) if qs_params else ""
        create_args = self._add_project(create_args, True)
        if GAE_ENABLED:
            try:
                req_options = {
                    'url': self.source_url + qs_str,
                    'method': urlfetch.POST,
                    'headers': SEND_JSON,
                    'data': create_args,
                    'files': {name: file_handler},
                    'validate_certificate': self.domain.verify
                }
                response = urlfetch.fetch(**req_options)
            except urlfetch.Error as exception:
                LOGGER.error("HTTP request error: %s",
                             str(exception))
                return maybe_save(resource_id, self.storage, code,
                                  location, resource, error)
        else:
            try:
                files = {"file": (name,
                                  file_handler,
                                  mimetypes.guess_type(name)[0])}
                files.update(create_args)
                multipart = MultipartEncoder(fields=files)
                response = requests.post( \
                    self.source_url,
                    params=qs_params,
                    headers={'Content-Type': multipart.content_type},
                    data=multipart, verify=self.domain.verify)
            except (requests.ConnectionError,
                    requests.Timeout,
                    requests.RequestException) as exc:
                LOGGER.error("HTTP request error: %s", str(exc))
                code = HTTP_INTERNAL_SERVER_ERROR
                return maybe_save(resource_id, self.storage, code,
                                  location, resource, error)
        try:
            code = response.status_code
            if code == HTTP_CREATED:
                location = response.headers['location']
                resource = json_load(response.content)
                resource_id = resource['resource']
                error = None
            elif code in [HTTP_BAD_REQUEST,
                          HTTP_UNAUTHORIZED,
                          HTTP_PAYMENT_REQUIRED,
                          HTTP_NOT_FOUND,
                          HTTP_TOO_MANY_REQUESTS]:
                error = json_load(response.content)
            else:
                LOGGER.error("Unexpected error (%s)", code)
                code = HTTP_INTERNAL_SERVER_ERROR

        except ValueError:
            LOGGER.error("Malformed response")

        return maybe_save(resource_id, self.storage, code,
                          location, resource, error)

    def clone_source(self, source,
                     args=None, wait_time=3, retries=10):
        """Creates a cloned source from an existing `source`

        """
        create_args = self._set_clone_from_args(
            source, "source", args=args, wait_time=wait_time, retries=retries)

        body = json.dumps(create_args)
        return self._create(self.source_url, body)

    def _create_composite(self, sources, args=None):
        """Creates a composite source from an existing `source` or list of
           sources

        """
        create_args = {}
        if args is not None:
            create_args.update(args)

        if not isinstance(sources, list):
            sources = [sources]

        source_ids = []
        for source in sources:
            # we accept full resource IDs or pure IDs and produce pure IDs
            try:
                source_id = get_source_id(source)
            except ValueError:
                source_id = None

            if source_id is None:
                pure_id = get_id(source)
                source_id = "source/%s" % pure_id
            else:
                pure_id = source_id.replace("source/", "")

            if pure_id is not None:
                source_ids.append(pure_id)
            else:
                raise Exception("A source or list of source ids"
                                " are needed to create a"
                                " source.")
        create_args.update({"sources": source_ids})

        body = json.dumps(create_args)
        return self._create(self.source_url, body)

    def create_source(self, path=None, args=None):
        """Creates a new source.

           The source can be a local file path or a URL.
           We also accept a pandas DataFrame as first argument
           TODO: add async load and progress bar in Python 3

        """

        if path is None:
            raise Exception('A local path or a valid URL must be provided.')

        if PANDAS_READY and isinstance(path, DataFrame):
            buffer = StringIO(path.to_csv(index=False))
            return self._create_local_source(file_name=buffer, args=args)
        if is_url(path):
            return self._create_remote_source(path, args=args)
        if isinstance(path, list):
            try:
                if all(get_id(item) is not None \
                       for item in path):
                    # list of sources
                    return self._create_composite(path, args=args)
            except ValueError:
                pass
            return self._create_inline_source(path, args=args)
        if isinstance(path, dict):
            return self._create_connector_source(path, args=args)
        try:
            if get_source_id(path) is not None:
            # cloning source
                return self.clone_source(path, args=args)
        except ValueError:
            pass
        return self._create_local_source(file_name=path, args=args)

    def create_annotated_source(self, annotations_file, args=None):
        """Creates a composite source for annotated images.

        Images are usually associated to other information, like labels or
        numeric fields, which can be regarded as additional attributes
        related to that image. The associated information can be described
        as annotations for each of the images. These annotations can be
        provided as a JSON file that contains the properties associated to
        each image and the name of the image file, that is used as foreign key.
        The meta information needed to create the structure of the composite
        source, such as the fields to be associated and their types,
        should also be included in the annotations file.
        This is an example of the expected structure of the annotations file:

            {"description": "Fruit images to test colour distributions",
             "images_file": "./fruits_hist.zip",
             "new_fields": [{"name": "new_label", "optype": "categorical"}],
             "source_id": null,
             "annotations": [
                {"file": "f1/fruits1f.png", "new_label": "True"},
                {"file": "f1/fruits1.png", "new_label": "False"},
                {"file": "f2/fruits2e.png", "new_label": "False"}]}

        The "images_file" attribute should contain the path to zip-compressed
        images file and the "annotations" attribute the corresponding
        annotations. The "new_fields" attribute should be a list of the fields
        used as annotations for the images.

        Also, if you prefer to keep your annotations in a separate file, you
        can point to that file in the "annotations" attribute:

            {"description": "Fruit images to test colour distributions",
             "images_file": "./fruits_hist.zip",
             "new_fields": [{"name": "new_label", "optype": "categorical"}],
             "source_id": null,
             "annotations": "./annotations_detail.json"}

        The created source will contain the fields associated to the
        uploaded images, plus an additional field named "new_label" with the
        values defined in this file.

        If a source has already been created from this collection of images,
        you can provide the ID of this source in the "source_id" attribute.
        Thus, the existing source will be updated to add the new annotations
        (if still open for editing) or will be cloned (if the source is
        closed for editing) and the new source will be updated . In both cases,
        images won't be uploaded when "source_id" is used.

        """

        if not os.path.exists(annotations_file):
            raise ValueError("A local path to a JSON file must be provided.")

        with open(annotations_file) as annotations_handler:
            annotations_info = json.load(annotations_handler)

        if annotations_info.get("images_file") is None:
            raise ValueError("Failed to find the `images_file` attribute "
                             "in the annotations file %s" % annotations_file)
        base_directory = os.path.dirname(annotations_file)
        zip_path = os.path.join(base_directory,
                                annotations_info.get("images_file"))
        if isinstance(annotations_info.get("annotations"), str):
            annotations = os.path.join(base_directory,
                                       annotations_info.get("annotations"))
        else:
            annotations = annotations_info.get("annotations")
        # check metadata file attributes
        if annotations_info.get("source_id") is None:
            # upload the compressed images
            source = self.create_source(zip_path, args=args)
            if not self.ok(source):
                raise IOError("A source could not be created for %s" %
                              zip_path)
            source_id = source["resource"]
        else:
            source_id = annotations_info.get("source_id")
        return self.update_composite_annotations(
            source_id, zip_path, annotations,
            new_fields=annotations_info.get("new_fields"))

    def update_composite_annotations(self, source, images_file,
                                     annotations, new_fields=None,
                                     source_changes=None):
        """Updates a composite source to add a list of annotations
        The annotations argument should contain annotations in a BigML-COCO
        syntax:

            [{"file": "image1.jpg",
              "label": "label1"}.
             {"file": "image2.jpg",
              "label": "label1"},
             {"file": "image3.jpg",
              "label": "label2"}]

        or point to a JSON file that contains that information,
        and the images_file argument should point to a zip file that
        contains the referrered images sorted as uploaded to build the source.

        If the attributes in the annotations file ("file" excluded) are not
        already defined in the composite source, the `new_fields` argument
        can be set to contain a list of the fields and types to be added

            [{"name": "label", "optype": "categorical"}]
        """
        if source_changes is None:
            source_changes = {}

        source_id = get_source_id(source)
        if source_id:
            source = self.get_source(source_id)
            if source.get("object", {}).get("closed"):
                source = self.clone_source(source_id)
        self.ok(source)
        # corresponding source IDs
        try:
            sources = source["object"]["sources"]
        except KeyError:
            raise ValueError("Failed to find the list of sources in the "
                             "created composite: %s." % source["resource"])
        try:
            with ZipFile(images_file) as zip_handler:
                file_list = zip_handler.namelist()
            file_list = filter_by_extension(file_list, IMAGE_EXTENSIONS)
        except IOError:
            raise ValueError("Failed to find the list of images in zip %s" %
                             images_file)

        file_to_source = dict(zip(file_list, sources))

        fields = Fields(source)

        # adding the annotation values
        if annotations:
            if isinstance(annotations, str):
                # path to external annotations file
                try:
                    with open(annotations) as \
                            annotations_handler:
                        annotations = json.load(annotations_handler)
                except IOError as exc:
                    raise ValueError("Failed to find annotations in %s" %
                                     exc)
            elif not isinstance(annotations, list):
                raise ValueError("The annotations attribute needs to contain"
                                 " a list of annotations or the path to "
                                 " a file with such a list.")
        if new_fields is None:
            new_fields = {}
            for annotation in annotations:
                for field, value in annotation.items():
                    if field != "file" and field not in new_fields:
                        new_fields[field] = infer_field_type(field, value)
            new_fields = list(new_fields.values())

        # creating new annotation fields, if absent
        if new_fields:
            field_names = [field["name"] for _, field in fields.fields.items()]
            changes = []
            for field_info in new_fields:
                if field_info.get("name") not in field_names:
                    changes.append(field_info)
            if changes:
                source_changes.update({"new_fields": changes})
        if source_changes:
            source = self.update_source(source["resource"], source_changes)
            self.ok(source)

        fields = Fields(source)

        changes = []
        changes_dict = {}
        for annotation in annotations:
            filename = annotation.get("file")
            try:
                _ = file_list.index(filename)
            except ValueError:
                LOGGER.error("WARNING: Could not find annotated file (%s)"
                             " in the composite's sources list", filename)
                continue
            for key in annotation.keys():
                if key == "file":
                    continue
                if key not in changes_dict:
                    changes_dict[key] = []
                value = annotation.get(key)
                changes_dict[key].append((value, file_to_source[filename]))

        #pylint: disable=locally-disabled,broad-except
        for field, values in changes_dict.items():
            try:
                optype = fields.fields[fields.field_id(field)]["optype"]
                if optype == "categorical":
                    sorted_values = sorted(values, key=lambda x: x[0])
                    old_value = None
                    source_ids = []
                    for value, source_id in sorted_values:
                        if value != old_value and old_value is not None:
                            changes.append({"field": field, "value": old_value,
                                            "components": source_ids})
                            source_ids = [source_id]
                            old_value = value
                        else:
                            source_ids.append(source_id)
                            if old_value is None:
                                old_value = value
                    changes.append({"field": field, "value": value,
                                    "components": source_ids})
                elif optype == "regions":
                    for value, source_id in values:
                        if isinstance(value, dict):
                            # dictionary should contain the bigml-coco format
                            value = compact_regions(value)
                        changes.append(
                            {"field": field,
                             "value": value,
                             "components": [source_id]})
                else:
                    for value, source_id in values:
                        changes.append(
                            {"field": field,
                             "value": value,
                             "components": [source_id]})
            except Exception:
                LOGGER.error("WARNING: Problem adding annotation to %s (%s)",
                             field, values)
                pass

        # we need to limit the amount of changes per update
        batches_number = int(len(changes) / MAX_CHANGES)
        for offset in range(0, batches_number + 1):
            new_batch = changes[
                offset * MAX_CHANGES: (offset + 1) * MAX_CHANGES]
            if new_batch:
                source = self.update_source(source,
                                            {"row_values": new_batch})+
                counter = 0
                while source["error"] is not None and counter < MAX_RETRIES:
                    # retrying in case update is temporarily unavailable
                    counter += 1
                    time.sleep(counter)
                    source = self.get_source(source)
                    self.ok(source)
                    source = self.update_source(source,
                                                {"row_values": new_batch})
                if source["error"] is not None:
                    LOGGER.error("WARNING: Some annotations were not"
                                 " updated (%s)",
                                  new_batch)
                if not self.ok(source):
                    raise Exception(
                        f"Failed to update {len(new_batch)} annotations.")
                time.sleep(0.1)

        return source

    def get_source(self, source, query_string=''):
        """Retrieves a remote source.
           The source parameter should be a string containing the
           source id or the dict returned by create_source.
           As source is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, thet function will
           return a dict that encloses the source values and state info
           available at the time it is called.
        """
        check_resource_type(source, SOURCE_PATH,
                            message="A source id is needed.")
        return self.get_resource(source, query_string=query_string)

    def source_is_ready(self, source):
        """Checks whether a source' status is FINISHED.

        """
        check_resource_type(source, SOURCE_PATH,
                            message="A source id is needed.")
        source = self.get_source(source)
        return resource_is_ready(source)

    def list_sources(self, query_string=''):
        """Lists all your remote sources.

        """
        return self._list(self.source_url, query_string)

    def update_source(self, source, changes):
        """Updates a source.

        Updates remote `source` with `changes'.

        """
        check_resource_type(source, SOURCE_PATH,
                            message="A source id is needed.")
        return self.update_resource(source, changes)

    def delete_source(self, source, query_string=''):
        """Deletes a remote source permanently.

        """
        check_resource_type(source, SOURCE_PATH,
                            message="A source id is needed.")
        return self.delete_resource(source, query_string=query_string)
