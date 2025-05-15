#!/bin/bash

# Если несколько постеров попадают в директорию, происходит разрешение коллизий и создается файл
# poster_kpId_random.jpg дополнительно к файлу poster_kpId.jpg
# Эти файлы нужно удалить.

# Navigate to the posters directory
#cd /root/projects/kinopolka/media/posters/

cd /home/stephan/projects/kinopolka/media/posters/

# Remove files with random strings in the name (e.g., poster_5449060_bHaOhRp.jpg)
for file in poster_*_*.jpg; do
    if [[ $file =~ poster_([0-9]+)_.*\.jpg ]]; then
        echo "Removing duplicate file: $file"
        rm "$file"
    fi
done

# List remaining files to verify
echo "Remaining files in media/posters/:"
ls -l