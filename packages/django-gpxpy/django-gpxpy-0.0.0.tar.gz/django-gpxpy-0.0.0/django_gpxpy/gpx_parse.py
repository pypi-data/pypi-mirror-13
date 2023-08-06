# -*- coding: utf-8 -*-

# Author: Petr Dlouhý <petr.dlouhy@auto-mat.cz>
#
# Copyright (C) 2016 o.s. Auto*Mat
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from django.core.exceptions import ValidationError
from django.contrib.gis.geos import Point, LineString, MultiLineString
import gpxpy
import logging
logger = logging.getLogger(__name__)


def parse_gpx(track):
    try:
        gpx = gpxpy.parse(track)
        if gpx.tracks:
            multiline = []
            for track in gpx.tracks:
                for segment in track.segments:
                    track_list_of_points = []
                    for point in segment.points:
                        point_in_segment = Point(point.longitude, point.latitude)
                        track_list_of_points.append(point_in_segment.coords)

                    if len(track_list_of_points) > 1:
                        multiline.append(LineString(track_list_of_points))
            return MultiLineString(multiline)
    except gpxpy.gpx.GPXException as e:
        logger.error("Valid GPX file: %s" % e)
        raise ValidationError(u"Vadný GPX soubor: %s" % e)
