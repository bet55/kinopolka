import os
from pathlib import Path
import re

from django.core.management.base import BaseCommand

from lists.models import Movie


class Command(BaseCommand):
    help = "Remove random suffixes from poster_local filenames and rename files in media/posters/"

    def handle(self, *args, **options):
        movies = Movie.mgr.all()
        total = movies.count()

        files_renamed = 0
        urls_renamed = 0
        skipped_count = 0
        error_count = 0

        print(f"Starting to process {total} movies...")

        for movie in movies:
            kp_id = movie.kp_id
            current_path = str(movie.poster_local)

            # Skip if poster_local is empty, default, or already correct
            if not current_path or current_path == "media/posters/default.png":
                print(f"Skipping movie {kp_id}: no poster or default")
                skipped_count += 1
                continue

            if re.match(rf"media/posters/poster_{kp_id}\.jpg$", current_path):
                print(f"Skipping movie {kp_id}: poster_local already correct")
                skipped_count += 1
                continue

            # Check for random suffix (e.g., poster_5449060_bHaOhRp.jpg)
            match = re.match(r"media/posters/poster_(\d+)_.*\.jpg$", current_path)

            if not match or int(match.group(1)) != kp_id:
                self.stdout.write(
                    self.style.WARNING(f"Skipping movie {kp_id}: invalid poster_local format ({current_path})")
                )
                skipped_count += 1
                continue

            # Paths
            old_file_path = Path(current_path)
            new_file_name = f"poster_{kp_id}.jpg"
            new_relative_path = f"posters/{new_file_name}"
            new_file_path = Path("media") / new_relative_path

            try:
                if not new_file_path.exists():
                    self.stdout.write(self.style.ERROR(f"movie {kp_id}: doesn't have correct file"))
                    error_count += 1
                    continue

                # Check if old file exists
                if old_file_path.exists():
                    # Rename the file on disk
                    os.rename(old_file_path, new_file_path)
                    files_renamed += 1

                # Update the model
                movie.poster_local = str(new_file_path)
                movie.save()
                urls_renamed += 1

                print(f"Updated movie {kp_id}: renamed {current_path} to {new_relative_path}")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error for movie {kp_id}: failed to update ({e!s})"))
                error_count += 1

        self.stdout.write(self.style.SUCCESS("Completed"))
        self.stdout.write(self.style.SUCCESS(f"posters updated: {urls_renamed} \t "))
        self.stdout.write(self.style.SUCCESS(f"files renamed: {files_renamed}\t "))
        self.stdout.write(self.style.SUCCESS(f"skipped: {skipped_count}\t "))
        self.stdout.write(self.style.ERROR(f"error: {error_count}"))
