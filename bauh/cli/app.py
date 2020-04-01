import os

import urllib3

from bauh import ROOT_DIR
from bauh.api.abstract.context import ApplicationContext
from bauh.api.http import HttpClient
from bauh.cli import __app_name__, cli_args
from bauh.cli.controller import CLIManager
from bauh.view.core import config, gems
from bauh.view.core.controller import GenericSoftwareManager
from bauh.view.core.downloader import AdaptableFileDownloader
from bauh.view.util import logs, util
from bauh.view.util.cache import DefaultMemoryCacheFactory
from bauh.view.util.disk import DefaultDiskCacheLoaderFactory
from bauh.view.util.translation import I18n


def main():
    if not os.getenv('PYTHONUNBUFFERED'):
        os.environ['PYTHONUNBUFFERED'] = '1'

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    args = cli_args.read()
    logger = logs.new_logger(__app_name__, False)

    app_config = config.read_config(update_file=True)
    http_client = HttpClient(logger)

    empty_i18n = I18n('en', {}, 'en', {})

    cache_factory = DefaultMemoryCacheFactory(expiration_time=0)

    context = ApplicationContext(i18n=empty_i18n,
                                 http_client=http_client,
                                 download_icons=bool(app_config['download']['icons']),
                                 app_root_dir=ROOT_DIR,
                                 cache_factory=cache_factory,
                                 disk_loader_factory=DefaultDiskCacheLoaderFactory(logger),
                                 logger=logger,
                                 distro=util.get_distro(),
                                 file_downloader=AdaptableFileDownloader(logger, bool(app_config['download']['multithreaded']),
                                                                         empty_i18n, http_client),
                                 app_name=__app_name__)

    managers = gems.load_managers(context=context, locale=empty_i18n.current_key, config=app_config, default_locale='en')

    cli = CLIManager(GenericSoftwareManager(managers, context=context, config=app_config))

    if args.command == 'updates':
        cli.list_updates(args.format)


if __name__ == '__main__':
    main()