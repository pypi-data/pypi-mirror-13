"""Classes module. These are objects **goldfinchsong** uses to keep state and perform business logic."""
from . import utils


class Manager:
    """
    Manages tweet posting through twitter API.

    Attributes:
        content (tuple): The class expects a tuple with a file name string
            and status text string.
        api: A tweepy API instance.
    """
    def __init__(self, credentials=None, image_directory=None, text_conversions=None):
        self.content = utils.load_content(image_directory, text_conversions)
        self.api = utils.access_api(credentials)

    def post_tweet(self):
        """
        Attempts tweet status post with image.

        Returns:
            tuple: A content tuple with image path and status text.
        Raises:
            Exception: Raises exception if content property is ``None``.
        """
        if self.content is not None:
            self.api.update_with_media(self.content[0], self.content[1])
            return self.content
        else:
            raise Exception("Can't post a tweet. No content available. Check image directory.")
