import logging
import asyncio
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from asgiref.sync import sync_to_async
import httpx
from lists.models import Movie

logger = logging.getLogger('kinopolka')
QUESTION_MARK_URL = "https://banner2.cleanpng.com/20180715/yag/aavjmwzok.webp"

class Command(BaseCommand):
    help = 'Download posters for all existing movies in the database and save to poster_local field'

    async def download_poster(self, movie, client):
        try:
            poster_url = movie.poster
            if not poster_url or poster_url == QUESTION_MARK_URL:
                logger.warning(f"No valid poster URL for movie {movie.kp_id}")
                movie.poster_local = 'posters/default.jpg'
                await sync_to_async(movie.save)()
                return movie.kp_id, False

            response = await client.get(poster_url)
            response.raise_for_status()
            file_name = f"poster_{movie.kp_id}.jpg"
            await sync_to_async(movie.poster_local.save)(file_name, ContentFile(response.content), save=True)
            logger.info(f"Downloaded and saved poster for movie {movie.kp_id}")
            return movie.kp_id, True
        except Exception as e:
            logger.error(f"Failed to download poster for movie {movie.kp_id}: {str(e)}")
            movie.poster_local = 'posters/default.jpg'
            await sync_to_async(movie.save)()
            return movie.kp_id, False

    @sync_to_async
    def get_movie_batch(self, start, end):
        return list(Movie.mgr.all()[start:end])

    def handle(self, *args, **options):
        movies = Movie.mgr.all()
        total = movies.count()
        success_count = 0
        failure_count = 0
        batch_size = 15

        self.stdout.write(f"Starting to download posters for {total} movies...")

        async def process_batch(batch):
            async with httpx.AsyncClient(timeout=10.0) as client:
                tasks = [self.download_poster(movie, client) for movie in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                return results

        for i in range(0, total, batch_size):
            batch = asyncio.run(self.get_movie_batch(i, i + batch_size))
            results = asyncio.run(process_batch(batch))
            for kp_id, success in results:
                if success:
                    success_count += 1
                else:
                    failure_count += 1

            self.stdout.write(f"Processed {min(i + batch_size, total)}/{total} movies...")

        self.stdout.write(self.style.SUCCESS(
            f"Completed: {success_count} posters downloaded successfully OPE, {failure_count} failed."
        ))