# Copyright (C) 2015 UCSC Computational Genomics Lab
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
import logging

log = logging.getLogger( __name__ )

old_match_hostname = None


def work_around_dots_in_bucket_names( ):
    """
    https://github.com/boto/boto/issues/2836
    """
    global old_match_hostname
    if old_match_hostname is None:
        import re
        import ssl
        try:
            old_match_hostname = ssl.match_hostname
        except AttributeError:
            log.warn( 'Failed to install workaround for dots in bucket names.' )
        else:
            hostname_re = re.compile( r'^(.*?)(\.s3(?:-[^.]+)?\.amazonaws\.com)$' )

            def new_match_hostname( cert, hostname ):
                match = hostname_re.match( hostname )
                if match:
                    hostname = match.group( 1 ).replace( '.', '' ) + match.group( 2 )
                return old_match_hostname( cert, hostname )

            ssl.match_hostname = new_match_hostname


def modify_metadata_retry( ):
    """
    https://github.com/BD2KGenomics/s3am/issues/16
    """
    from boto import config

    def inject_default( name, default ):
        section = 'Boto'
        value = config.get( section, name )

        if value != default:
            if not config.has_section( section ):
                config.add_section( section )
            config.set( section, name, default )

    inject_default( 'metadata_service_timeout', '5.0' )
    inject_default( 'metadata_service_num_attempts', '3' )
