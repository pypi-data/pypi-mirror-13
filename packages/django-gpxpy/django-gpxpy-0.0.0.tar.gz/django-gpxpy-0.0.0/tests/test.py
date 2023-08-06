from django_gpxpy.gpx_parse import parse_gpx
from django.test import TestCase
from django.core.exceptions import ValidationError

class DjangoGpxPyTests(TestCase):
    def test_gpx_parsing(self):
        """
        test if the admin page with RelatedFieldRadioFilter filters loads succesfully
        """
        with open("tests/test_data/test_track.gpx", "r") as f:
            multilinestring = parse_gpx(f)
        self.assertEquals(multilinestring.num_geom, 26)

    def test_bad_file_parsing(self):
        """
        test if the admin page with RelatedFieldRadioFilter filters loads succesfully
        """
        with self.assertRaises(ValidationError):
            with open("tests/test_data/test_bad_file.gpx", "r") as f:
                multilinestring = parse_gpx(f)
