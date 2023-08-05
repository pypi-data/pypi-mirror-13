"""Command line interface module."""
from collections import OrderedDict
import configparser
from logging import config as log_config
import click
from .classes import Manager
from .settings import LOGGER_CONFIG


def get_image_directory(command_line_input, active_configuration):
    """
    Provides path to image directory.

    Arguments:
        command_line_input (str | ``None``): A path that may optionally be submitted by user. A string
            or ``None`` are expected types.
        active_configuration (dict): Active configuration options.

    Returns:
        str: A path to the image directory. Default: ``images``
    """
    if command_line_input is not None:
        return command_line_input
    elif 'image_directory' in active_configuration:
        return active_configuration['image_directory']
    return 'images'


def parse_configuration(config_parser):
    """
    Extracts credential and text conversion information.

    Args:
        config_parser: A ``ConfigParser`` from the standard library
            loaded with local configuration file.

    Returns:
        dict: The returned dict containts twitter credentials, any text conversions, and
            any image configuration information made available.
    """
    active_configuration = dict()
    active_configuration['credentials'] = config_parser['goldfinchsong']
    if config_parser.has_section('goldfinchsong.log'):
        if 'log_level' in config_parser['goldfinchsong.log']:
            active_configuration['log_level'] = config_parser['goldfinchsong.log']['log_level']
            LOGGER_CONFIG['loggers']['goldfinchsong']['level'] = active_configuration['log_level']
            log_config.dictConfig(LOGGER_CONFIG)
    active_configuration['text_conversions'] = None
    if config_parser.has_section('goldfinchsong.conversions'):
        pairings = config_parser['goldfinchsong.conversions']
        text_conversions = OrderedDict()
        for abbreviated, original in pairings.items():
            text_conversions[original] = abbreviated
        active_configuration['text_conversions'] = text_conversions
    if config_parser.has_section('goldfinchsong.images'):
        images_configuration = config_parser['goldfinchsong.images']
        if 'image_directory' in images_configuration:
            active_configuration['image_directory'] = images_configuration['image_directory']
    return active_configuration


@click.command()
@click.option('--action', default='post')
@click.option('--conf', default='goldfinchsong.ini')
@click.option('--images', default=None)
def run(action, conf, images):
    """
    Uploads an image tweet.

    Arguments:
        action (str): An action name.
        conf (str): File path for a configuration file. By default, this
            function looks for ``goldfinchsong.ini`` under the directory from
            which the user executes the function.
        images (str): File path to a directory with images that will be uploaded by tweets.
    """
    config_parser = configparser.ConfigParser()
    config_parser.optionxform = str
    config_parser.read(conf)
    if config_parser.has_section('goldfinchsong'):
        active_configuration = parse_configuration(config_parser)
        if action == 'post':
            image_directory = get_image_directory(images, active_configuration)
            manager = Manager(active_configuration['credentials'],
                              image_directory,
                              active_configuration['text_conversions'])
            manager.post_tweet()
        else:
            print('That command action is not supported.')
    else:
        print('Twitter credentials must be placed within ini file.')