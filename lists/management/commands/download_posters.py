import asyncio
from pathlib import Path

from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
import httpx

from lists.models import Movie


QUESTION_MARK_URL = "https://banner2.cleanpng.com/20180715/yag/aavjmwzok.webp"
DEFAULT_POSTER = "posters/default.jpg"


class Command(BaseCommand):
    help = "Link existing posters in media/posters/ to poster_local or download missing posters"

    async def link_existing_poster(self, movie, kp_id):
        # Check for existing poster file in media/posters/
        for ext in [".jpg", ".png"]:
            poster_path = Path(f"media/posters/poster_{kp_id}{ext}")
            if poster_path.exists():
                file_name = f"poster_{kp_id}{ext}"
                # Update poster_local to reference the existing file
                await sync_to_async(movie.poster_local.save)(
                    file_name, ContentFile(poster_path.read_bytes()), save=True
                )
                self.stdout.write(f"Linked existing poster for movie {kp_id}: {file_name}")
                return True
        return False

    async def download_poster(self, movie, client, max_retries=3):
        kp_id = movie.kp_id

        # Skip if poster_local is already set and file exists
        if movie.poster_local and str(movie.poster_local) != DEFAULT_POSTER:
            poster_path = Path(movie.poster_local.path)
            if poster_path.exists():
                self.stdout.write(f"Skipping movie {kp_id}: poster_local already exists")
                return kp_id, True

        # Check for existing file in media/posters/
        if await self.link_existing_poster(movie, kp_id):
            return kp_id, True

        # Skip if no valid poster URL
        if not movie.poster or movie.poster == QUESTION_MARK_URL:
            self.stdout.write(self.style.WARNING(f"No valid poster URL for movie {kp_id}"))
            movie.poster_local = None
            await sync_to_async(movie.save)()
            return kp_id, False

        # Download poster
        for attempt in range(1, max_retries + 1):
            try:
                response = await client.get(movie.poster)
                response.raise_for_status()
                content_type = response.headers.get("content-type", "image/jpeg")
                extension = ".jpg"  # Use .jpg for JPEG posters
                file_name = f"poster_{kp_id}{extension}"
                await sync_to_async(movie.poster_local.save)(file_name, ContentFile(response.content), save=True)
                self.stdout.write(f"Downloaded and saved poster for movie {kp_id}")
                return kp_id, True
            except httpx.HTTPStatusError as e:
                if e.response.status_code in (404, 403):
                    self.stdout.write(self.style.WARNING(f"Poster not found for movie {kp_id}: {e!s}"))
                    break  # No retry for 404 or 403
                elif e.response.status_code == 429:
                    self.stdout.write(
                        self.style.WARNING(f"Rate limit hit for movie {kp_id}, attempt {attempt}/{max_retries}")
                    )
                    if attempt < max_retries:
                        await asyncio.sleep(2**attempt)  # Exponential backoff
                    else:
                        self.stdout.write(self.style.ERROR(f"Max retries reached for movie {kp_id}: {e!s}"))
                        break
                else:
                    self.stdout.write(self.style.ERROR(f"HTTP error for movie {kp_id}: {e!s}"))
                    break
            except (httpx.RequestError, httpx.TimeoutException) as e:
                self.stdout.write(
                    self.style.WARNING(f"Network error for movie {kp_id}, attempt {attempt}/{max_retries}: {e!s}")
                )
                if attempt < max_retries:
                    await asyncio.sleep(2**attempt)
                else:
                    self.stdout.write(self.style.ERROR(f"Max retries reached for movie {kp_id}: {e!s}"))
                    break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Unexpected error for movie {kp_id}: {e!s}"))
                break

        movie.poster_local = None  # Clear to use model default
        await sync_to_async(movie.save)()
        return kp_id, False

    @sync_to_async
    def get_movie_batch(self, start, end):
        return list(Movie.mgr.all()[start:end])

    def handle(self, *args, **options):
        movies = Movie.mgr.all()
        total = movies.count()
        success_count = 0
        failure_count = 0
        batch_size = 10
        batch_delay = 1.5

        self.stdout.write(f"Starting to process posters for {total} movies...")

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
            if i + batch_size < total:
                asyncio.run(asyncio.sleep(batch_delay))

        self.stdout.write(
            self.style.SUCCESS(f"Completed: {success_count} posters processed successfully, {failure_count} failed.")
        )
