import subprocess

from django.core.management.base import BaseCommand

from pemors.titles.utils import UserRatingPreprocessor


class Command(BaseCommand):
    help = "Load anonymous ratings"
    file_url = "https://raw.githubusercontent.com/sidooms/MovieTweetings/master/latest/ratings.dat"
    output_file = "ratings.dat"

    def handle(self, *args, **options):
        subprocess.check_call(
            f"curl {self.file_url} --output downloads/{self.output_file}", shell=True
        )
        UserRatingPreprocessor(
            file_name=self.output_file, is_bulk=True, stdout=self.stdout
        ).process(delimiter=":")
