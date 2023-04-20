# gelbooruScaper
Simple mass image/videoall downloader for gelbooru.

## Keep in mind this is against Gelbooru's TOS!
Use at your own risk.

## Use
 - First enter name of download (all images and the directory will be named this)
 - Secondly enter the gelbooru url you want to start scraping from e.g .`` https://gelbooru.com/index.php?page=post&s=list&tags=all`` But it is possible to start from any page other than the start.
 - Then the amount of pages to scrape (a full page contains **42** images/videos)
 - Lastly comfirm you selections (***alt+q*** to exit)

## Settings
Upon running ``scraper.py`` settings.json will be created in the same directory. So if the file is broken in a way you can just delete it to create a working one.

 - ``amt_download_threads`` the amount of threads used when downloading, the higher the faster the download but the more cpu and network.
 - ``shutdown_on_completion`` whether the computer shuts down when finished scraping.
 - ``clear_console`` only works on windows
 - ``mp4_or_webm`` options for downloading videos, choose one.
 - ``save_path`` **default** is ``current-directory/saves/``, when changing this value make sure the path has **double "\\"** or / e.g. ``C:/Users/saves`` or ``C:/Users/saves``
 - ``average_file_size_mb`` can be calibrated by using ``averageFileSizeCalculator.py`` but is only used for estimates.
 - ``invalid_path_characters`` is for name validation and be added to but isn't very important.
