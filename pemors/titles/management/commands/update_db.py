import subprocess

from django.core.management.base import BaseCommand
from django.db import transaction

from pemors.titles.utils import (
    AkaPreprocessor,
    CrewPreprocessor,
    PersonPreprocessor,
    RatingPreprocessor,
    TitlePreprocessor,
)


class Command(BaseCommand):
    help = "Fetch and save all data from IMDb"
    file_names = [
        "title.basics.tsv",
        "title.ratings.tsv",
        "title.akas.tsv",
        "name.basics.tsv",
        "title.principals.tsv",
    ]
    base_url = "https://datasets.imdbws.com/"

    def add_arguments(self, parser):
        parser.add_argument(
            "--new",
            help="Use bulk create to speed up the model creation.",
        )
        parser.add_argument(
            "--skip", nargs="+", type=int, help="Skip a process from 0 to 4."
        )

    def handle(self, *args, **options):
        subprocess.check_call("rm -rf downloads", shell=True)
        for i, file_name in enumerate(self.file_names):
            if options["skip"] and i in options.get("skip", []):
                self.stdout.write(f"Skipping {file_name}:")
                continue
            self.stdout.write(f"Downlading {file_name}:")
            subprocess.check_call(
                f"curl {self.base_url}{file_name}.gz --output downloads/{file_name}.gz --create-dirs",
                shell=True,
            )

            self.stdout.write(f"\tDecompresing {file_name}...")
            subprocess.check_call(f"gzip -d downloads/{file_name}.gz", shell=True)

            self.process_file(i, True if options["new"] else False)

    def process_file(self, i, is_bulk):
        self.stdout.write(
            f"\tProcessing {self.file_names[i]} {'in bulk' if is_bulk else ''}"
        )

        if i == 0:
            self.process_title_basics(i, is_bulk)
        elif i == 1:
            self.process_title_ratings(i, is_bulk)
        elif i == 2:
            self.process_title_akas(i, is_bulk)
        elif i == 3:
            self.process_name_basics(i, is_bulk)
        elif i == 4:
            self.process_title_crew(i, is_bulk)

    @transaction.atomic
    def process_title_basics(self, file_id, is_bulk):
        TitlePreprocessor(
            file_name=self.file_names[file_id], is_bulk=is_bulk, stdout=self.stdout
        ).process(delimiter="\t")

    @transaction.atomic
    def process_title_ratings(self, file_id, is_bulk):
        RatingPreprocessor(
            file_name=self.file_names[file_id], is_bulk=is_bulk, stdout=self.stdout
        ).process(delimiter="\t")

    @transaction.atomic
    def process_title_akas(self, file_id, is_bulk):
        AkaPreprocessor(
            file_name=self.file_names[file_id], is_bulk=is_bulk, stdout=self.stdout
        ).process(delimiter="\t")

    @transaction.atomic
    def process_name_basics(self, file_id, is_bulk):
        PersonPreprocessor(
            file_name=self.file_names[file_id], is_bulk=is_bulk, stdout=self.stdout
        ).process(delimiter="\t")

    @transaction.atomic
    def process_title_crew(self, file_id, is_bulk):
        CrewPreprocessor(
            file_name=self.file_names[file_id], is_bulk=is_bulk, stdout=self.stdout
        ).process(delimiter="\t")
