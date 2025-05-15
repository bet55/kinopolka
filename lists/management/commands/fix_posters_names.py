import re
from django.core.management.base import BaseCommand
from lists.models import Movie
from pathlib import Path
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = 'Remove random suffixes from poster_local filenames and rename files in media/posters/'

    def handle(self, *args, **options):
        movies = Movie.mgr.all()
        total = movies.count()
        updated_count = 0
        skipped_count = 0
        error_count = 0

        self.stdout.write(f"Starting to process {total} movies...")

        for movie in movies:
            kp_id = movie.kp_id
            current_path = str(movie.poster_local) if movie.poster_local else ''

            # Skip if poster_local is empty, default, or already correct
            if not current_path or current_path == 'media/posters/default.jpg':
                self.stdout.write(f"Skipping movie {kp_id}: no poster or default")
                skipped_count += 1
                continue
            if re.match(rf'^media/posters/poster_{kp_id}\.jpg$', current_path):
                self.stdout.write(f"Skipping movie {kp_id}: poster_local already correct")
                skipped_count += 1
                continue

            # Check for random suffix (e.g., poster_5449060_bHaOhRp.jpg)
            match = re.match(r'^media/posters/poster_(\d+)_.*\.jpg$', current_path)
            if not match or int(match.group(1)) != kp_id:
                self.stdout.write(
                    self.style.WARNING(f"Skipping movie {kp_id}: invalid poster_local format ({current_path})"))
                skipped_count += 1
                continue

            # Paths
            new_file_name = f"poster_{kp_id}.jpg"
            new_file_path = Path(f'media/posters/{new_file_name}')

            try:
                # Update poster_local
                movie.poster_local.save(new_file_name, ContentFile(new_file_path.read_bytes()), save=True)
                self.stdout.write(f"Updated movie {kp_id}: renamed {current_path} to posters/{new_file_name}")
                updated_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error for movie {kp_id}: failed to update ({str(e)})"))
                error_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Completed: {updated_count} posters updated, {skipped_count} skipped, {error_count} errors."
        ))