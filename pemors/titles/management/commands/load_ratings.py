import subprocess

from django.core.management.base import BaseCommand

from pemors.titles.utils import UserPreprocessor, UserRatingPreprocessor


class Command(BaseCommand):
    help = "Load anonymous ratings"
    ratings_url = "https://raw.githubusercontent.com/sidooms/MovieTweetings/master/latest/ratings.dat"
    users_url = "https://raw.githubusercontent.com/sidooms/MovieTweetings/master/latest/users.dat"
    ratings_output_file = "ratings.dat"
    users_output_file = "users.dat"

    def handle(self, *args, **options):
        subprocess.check_call(
            f"curl {self.users_url} --output downloads/{self.users_output_file}",
            shell=True,
        )
        UserPreprocessor(
            file_name=self.users_output_file, is_bulk=True, stdout=self.stdout
        ).process(delimiter=":")
        subprocess.check_call(
            f"curl {self.ratings_url} --output downloads/{self.ratings_output_file}",
            shell=True,
        )
        UserRatingPreprocessor(
            file_name=self.ratings_output_file, is_bulk=True, stdout=self.stdout
        ).process(delimiter=":")
