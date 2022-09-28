import csv
import subprocess
import sys

from django.conf import settings
from django.db import transaction
from tqdm import tqdm

from pemors.titles.models import (
    Aka,
    Crew,
    Genre,
    KnownFor,
    Person,
    Rating,
    Title,
    TitleGenre,
    UserRating,
)
from pemors.users.models import User

csv.field_size_limit(sys.maxsize)

BATCH_SIZE = 1000


class Preprocesor:
    def __init__(self, file_name, is_bulk, stdout):
        self.file_name = file_name
        self.is_bulk = is_bulk
        self.stdout = stdout

    @transaction.atomic
    def process(self, delimiter):
        self.rename()
        with open(f"downloads/{self.file_name}") as file:
            self.stdout.write("\tLoading file in memory...")
            data = file.readlines()
            n = len(data)
            reader = csv.DictReader(data, delimiter=delimiter)

            if self.is_bulk:
                self.process_in_bulk(reader, n)
            else:
                self.process_no_bulk(reader, n)

    def rename(self):
        raise NotImplementedError("Subclasses should implement this method")

    def process_in_bulk(self, file_name, reader):
        raise NotImplementedError("Subclasses should implement this method")

    def process_no_bulk(self, reader, n):
        raise NotImplementedError("Subclasses should implement this method")


class TitlePreprocessor(Preprocesor):
    def rename(self):
        self.stdout.write("\tRenaming columns...")
        subprocess.check_call(
            f'sed -i "1s/tconst/id/" downloads/{self.file_name}', shell=True
        )
        subprocess.check_call(
            f'sed -i "1s/titleType/type/" downloads/{self.file_name}', shell=True
        )
        subprocess.check_call(
            f'sed -i "1s/primaryTitle/primary_title/" downloads/{self.file_name}',
            shell=True,
        )
        subprocess.check_call(
            f'sed -i "1s/originalTitle/original_title/" downloads/{self.file_name}',
            shell=True,
        )
        subprocess.check_call(
            f'sed -i "1s/startYear/start_year/" downloads/{self.file_name}', shell=True
        )
        subprocess.check_call(
            f'sed -i "1s/runtimeMinutes/runtime/" downloads/{self.file_name}',
            shell=True,
        )

    def process_in_bulk(self, reader, n):
        titles = []
        titles_genres = []
        genre_index = {}
        for data in tqdm(reader, total=n):
            title_genres = data.pop("genres")
            if not self.validate_title(data):
                continue

            data["start_year"] = (
                None if data["start_year"] == "\\N" else int(data["start_year"])
            )
            title = Title(**data)
            titles.append(title)

            self.create_title_genres(titles_genres, title_genres, title, genre_index)

            if len(titles_genres) + len(titles) > BATCH_SIZE:
                Title.objects.bulk_create(titles)
                TitleGenre.objects.bulk_create(titles_genres)
                titles = []
                titles_genres = []

        Title.objects.bulk_create(titles)
        TitleGenre.objects.bulk_create(titles_genres)

    def create_title_genres(self, titles_genres, title_genres, title, genre_index):
        title_genres = title_genres.split(",")
        for genre_name in title_genres:
            if genre_name == "\\N":
                continue
            genre = self.found_or_create_genre(genre_name, genre_index)
            titles_genres.append(TitleGenre(title=title, genre=genre))

    def found_or_create_genre(self, genre_name, genre_index):
        if genre_index.get(genre_name, False):
            return genre_index[genre_name]
        genre = Genre.objects.create(name=genre_name)
        genre_index[genre_name] = genre
        return genre

    def validate_title(self, data):
        data.pop("endYear")
        data.pop("isAdult")
        if data["type"] not in ["movie", "tvMovie"]:
            return False
        try:
            data["runtime"] = None if data["runtime"] == "\\N" else int(data["runtime"])
        except ValueError:
            self.stdout.write(f"\tSkipped {data}")
            return False

        return True

    def process_no_bulk(self, file_id, reader):
        return NotImplementedError


class RatingPreprocessor(Preprocesor):
    def rename(self):
        self.stdout.write("\tRenaming columns...")
        subprocess.check_call(
            f'sed -i "1s/tconst/title_id/" downloads/{self.file_name}', shell=True
        )
        subprocess.check_call(
            f'sed -i "1s/averageRating/average_rating/" downloads/{self.file_name}',
            shell=True,
        )
        subprocess.check_call(
            f'sed -i "1s/numVotes/num_votes/" downloads/{self.file_name}', shell=True
        )

    def process_in_bulk(self, reader, n):
        ratings = []
        titles = {title.id: title for title in Title.objects.all()}
        for data in tqdm(reader, total=n):

            if not self.validate(data, titles):
                continue

            rating = Rating(**data)
            ratings.append(rating)

            if len(ratings) > BATCH_SIZE:
                Rating.objects.bulk_create(ratings)
                ratings = []

        Rating.objects.bulk_create(ratings)

    def process_no_bulk(self, file_id, reader):
        return NotImplementedError

    def validate(self, data, titles):
        return titles.get(data["title_id"], False)


class AkaPreprocessor(Preprocesor):
    def rename(self):
        self.stdout.write("\tRenaming columns...")
        subprocess.check_call(
            f'sed -i "1s/titleId/title_id/" downloads/{self.file_name}', shell=True
        )
        subprocess.check_call(
            f'sed -i "1s/title/value/2" downloads/{self.file_name}', shell=True
        )
        subprocess.check_call(
            f'sed -i "1s/isOriginalTitle/is_original_title/" downloads/{self.file_name}',
            shell=True,
        )

    def process_in_bulk(self, reader, n):
        akas = []
        self.stdout.write("\tFetching movies...")
        titles = {title.id: title for title in Title.objects.all()}

        for data in tqdm(reader, total=n):

            if not self.validate(data, titles):
                continue

            aka = Aka(**data)
            akas.append(aka)

            if len(akas) > BATCH_SIZE:
                Aka.objects.bulk_create(akas)
                akas = []

        Aka.objects.bulk_create(akas)

    def process_no_bulk(self, file_id, reader):
        return NotImplementedError

    def validate(self, data, titles):
        data.pop("ordering")
        data["is_original_title"] = data["is_original_title"] == "1"
        return titles.get(data["title_id"], False)


class PersonPreprocessor(Preprocesor):
    def rename(self):
        self.stdout.write("\tRenaming columns...")
        subprocess.check_call(
            f'sed -i "1s/nconst/id/" downloads/{self.file_name}', shell=True
        )
        subprocess.check_call(
            f'sed -i "1s/primaryName/primary_name/" downloads/{self.file_name}',
            shell=True,
        )
        subprocess.check_call(
            f'sed -i "1s/birthYear/birth_year/" downloads/{self.file_name}', shell=True
        )
        subprocess.check_call(
            f'sed -i "1s/deathYear/death_year/" downloads/{self.file_name}', shell=True
        )
        subprocess.check_call(
            f'sed -i "1s/primaryProfession/profession/" downloads/{self.file_name}',
            shell=True,
        )

    def process_in_bulk(self, reader, n):
        people = []
        known_for = []
        self.stdout.write("\tFetching person...")
        titles = {title.id: title for title in Title.objects.all()}

        for data in tqdm(reader, total=n):
            i_known_for = data.pop("knownForTitles")
            data["death_year"] = (
                None if data["death_year"] == "\\N" else int(data["death_year"])
            )
            data["birth_year"] = (
                None if data["birth_year"] == "\\N" else int(data["birth_year"])
            )
            person = Person(**data)
            people.append(person)

            self.create_title_genres(known_for, i_known_for, person, titles)

            if len(people) > BATCH_SIZE or len(known_for) > BATCH_SIZE:
                Person.objects.bulk_create(people)
                KnownFor.objects.bulk_create(known_for, ignore_conflicts=True)
                known_for = []
                people = []

        Person.objects.bulk_create(people, ignore_conflicts=True)

    def process_no_bulk(self, file_id, reader):
        return NotImplementedError

    def create_title_genres(self, known_for, i_known_for, person, titles):
        i_known_for = i_known_for.split(",")
        for title_id in i_known_for:
            if titles.get(title_id, False):
                known_for.append(KnownFor(person=person, title_id=title_id))


class CrewPreprocessor(Preprocesor):
    def rename(self):
        self.stdout.write("\tRenaming columns...")
        subprocess.check_call(
            f'sed -i "1s/tconst/title_id/" downloads/{self.file_name}', shell=True
        )
        subprocess.check_call(
            f'sed -i "1s/nconst/person_id/" downloads/{self.file_name}', shell=True
        )

    def process_in_bulk(self, reader, n):
        crews = []
        self.stdout.write("\tFetching crew...")
        titles = {
            title["id"]: title["id"] for title in Title.objects.all().values("id")
        }
        people = {
            person["id"]: person["id"] for person in Person.objects.all().values("id")
        }

        for data in tqdm(reader, total=n):

            if not self.validate(data, titles, people):
                continue

            crew = Crew(**data)
            crews.append(crew)

            if len(crews) > BATCH_SIZE:
                Crew.objects.bulk_create(crews)
                crews = []

        Crew.objects.bulk_create(crews)

    def process_no_bulk(self, file_id, reader):
        return NotImplementedError

    def validate(self, data, titles, people):
        data.pop("ordering")
        return titles.get(data["title_id"], False) and people.get(
            data["person_id"], False
        )


class UserPreprocessor(Preprocesor):
    def rename(self):
        self.stdout.write("\tRenaming columns...")

        subprocess.check_call(
            f' sed -i "1i user_id::twitter_id" downloads/{self.file_name}',
            shell=True,
        )

    def process_in_bulk(self, reader, n):
        users = []

        for data in tqdm(reader, total=n):
            user = User(
                username=generate_username(data.get("user_id")),
                email=generate_username(data.get("user_id")) + "@pemors.com",
            )
            users.append(user)

            if len(users) > BATCH_SIZE:
                User.objects.bulk_create(users)
                users = []

        User.objects.bulk_create(users)

    def process_no_bulk(self, file_id, reader):
        return NotImplementedError


class UserRatingPreprocessor(Preprocesor):
    def rename(self):
        self.stdout.write("\tRenaming columns...")

        subprocess.check_call(
            f' sed -i "1i user_id::title_id::rating::rating_timestamp" downloads/{self.file_name}',
            shell=True,
        )

    def process_in_bulk(self, reader, n):
        user_ratings = []
        self.stdout.write("\tFetching movies...")
        titles = {title.id: title for title in Title.objects.all()}
        synthetic_users = {
            user.username: user.id
            for user in User.objects.filter(
                username__startswith=settings.SYNTETHIC_USER_PATTERN
            )
        }

        for data in tqdm(reader, total=n):
            if not self.validate(data, titles):
                continue
            user_rating = UserRating(
                rating=data.get("rating"),
                user_id=synthetic_users.get(generate_username(data.get("user_id"))),
                title_id=data.get("title_id"),
            )
            user_ratings.append(user_rating)

            if len(user_ratings) > BATCH_SIZE:
                UserRating.objects.bulk_create(user_ratings)
                user_ratings = []

        UserRating.objects.bulk_create(user_ratings)

    def process_no_bulk(self, file_id, reader):
        return NotImplementedError

    def validate(self, data, titles):
        data.pop("")
        data.pop("rating_timestamp")
        if not titles.get(f"tt{data['title_id']}", False):
            return False
        else:
            data["title_id"] = f"tt{data['title_id']}"
            return True


def generate_username(user_id):
    return f"{settings.SYNTETHIC_USER_PATTERN}{user_id}"
